// Terrestrial Tribulations: ModSync
// Runs as Prism Launcher's pre-launch command (Java 17 single-file source mode):
//   "$INST_JAVA" "$INST_MC_DIR/tt-sync/ModSync.java"
// Reads tt-sync/mods.json, resolves every mod (and its required dependencies) from the Modrinth API
// for the pack's Minecraft version and loader, downloads missing jars into mods/, checks the SHA-1,
// and pins the resolved versions in tt-sync/lock.json so later launches are reproducible.
// It never blocks the launch: problems are reported in tt-sync/sync-report.txt.
import java.io.*;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.*;

public class ModSync {
    static final String API = System.getenv().getOrDefault("TT_MODRINTH_API", "https://api.modrinth.com/v2"); // override only for testing
    static final String UA = "Mavros13/Terrestrial-Tribulations/ModSync (github.com/Mavros13/Terrestrial-Tribulations)";
    static final HttpClient HTTP = HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NORMAL).connectTimeout(Duration.ofSeconds(20)).build();

    static Path mcDir, syncDir, modsDir;
    static String mcVersion, loader;
    static final List<String> report = new ArrayList<>();

    public static void main(String[] args) {
        try {
            run(args);
        } catch (Throwable t) {
            log("ModSync failed: " + t);
            report.add("FATAL: " + t);
        }
        writeReport();
        System.exit(0); // never block the launch
    }

    static void run(String[] args) throws Exception {
        String dir = args.length > 0 ? args[0] : System.getenv("INST_MC_DIR");
        mcDir = Paths.get(dir != null ? dir : ".").toAbsolutePath();
        syncDir = mcDir.resolve("tt-sync");
        modsDir = mcDir.resolve("mods");
        Files.createDirectories(modsDir);

        Map<String, Object> cfg = obj(Json.parse(Files.readString(syncDir.resolve("mods.json"))));
        mcVersion = str(cfg.get("minecraft"));
        loader = str(cfg.get("loader"));
        String stage = readStage();
        log("Terrestrial Tribulations ModSync, MC " + mcVersion + " " + loader + ", stage " + stage);

        Path lockFile = syncDir.resolve("lock.json");
        Map<String, Object> lock = Files.exists(lockFile) ? obj(Json.parse(Files.readString(lockFile))) : new LinkedHashMap<>();

        // project_id -> resolved version entry
        Map<String, Map<String, Object>> resolved = new LinkedHashMap<>();
        Deque<String[]> queue = new ArrayDeque<>(); // {idOrSlug, displayName, pinnedVersion, curseforgeSlug}
        List<Map<String, Object>> manual = new ArrayList<>();

        for (Object o : list(cfg.get("mods"))) {
            Map<String, Object> m = obj(o);
            if (str(m.get("stage")).compareTo(stage) > 0) continue;
            if (Boolean.TRUE.equals(m.get("disabled"))) continue;
            String mr = str(m.get("modrinth"));
            if (mr == null || mr.isEmpty()) { manual.add(m); continue; }
            queue.add(new String[]{mr, str(m.get("name")), str(m.get("version")), str(m.get("curseforge")), str(m.get("match"))});
        }

        Set<String> seenKeys = new HashSet<>();
        while (!queue.isEmpty()) {
            String[] q = queue.poll();
            if (!seenKeys.add(q[0])) continue;
            Map<String, Object> ver = lockedOrFetch(lock, q[0], q[2]);
            if (ver == null) {
                if (q.length > 3 && q[3] != null) {
                    Map<String, Object> mm = new LinkedHashMap<>(); mm.put("name", q[1]); mm.put("curseforge", q[3]); mm.put("match", q[4]); manual.add(mm);
                } else report.add("NOT FOUND on Modrinth for " + mcVersion + "/" + loader + ": " + q[1] + " (" + q[0] + ")");
                continue;
            }
            String pid = str(ver.get("project_id"));
            if (resolved.containsKey(pid)) continue;
            resolved.put(pid, ver);
            lock.put(q[0], ver);
            for (Object d : list(ver.get("dependencies"))) {
                Map<String, Object> dep = obj(d);
                if (!"required".equals(dep.get("dependency_type"))) continue;
                String dpid = str(dep.get("project_id"));
                if (dpid != null && !resolved.containsKey(dpid)) queue.add(new String[]{dpid, "dependency of " + q[1], null, null, null});
            }
        }

        // Download.
        Set<String> wanted = new LinkedHashSet<>();
        for (Map<String, Object> v : resolved.values()) {
            String fn = str(v.get("filename"));
            wanted.add(fn);
            Path target = modsDir.resolve(fn);
            if (Files.exists(target) && sha1(target).equalsIgnoreCase(str(v.get("sha1")))) continue;
            log("Downloading " + fn);
            Path tmp = modsDir.resolve(fn + ".part");
            HttpResponse<Path> r = HTTP.send(HttpRequest.newBuilder(URI.create(str(v.get("url"))))
                    .header("User-Agent", UA).timeout(Duration.ofMinutes(5)).build(), HttpResponse.BodyHandlers.ofFile(tmp));
            if (r.statusCode() != 200) { report.add("DOWNLOAD FAILED (" + r.statusCode() + "): " + fn); Files.deleteIfExists(tmp); continue; }
            if (!sha1(tmp).equalsIgnoreCase(str(v.get("sha1")))) { report.add("HASH MISMATCH: " + fn); Files.deleteIfExists(tmp); continue; }
            Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING);
        }

        // Remove jars this tool installed earlier that are no longer wanted (e.g. stage lowered, version changed).
        Path installedFile = syncDir.resolve("installed.json");
        if (Files.exists(installedFile)) {
            for (Object o : list(Json.parse(Files.readString(installedFile)))) {
                String fn = str(o);
                if (!wanted.contains(fn) && Files.deleteIfExists(modsDir.resolve(fn))) log("Removed " + fn);
            }
        }
        Files.writeString(installedFile, Json.write(new ArrayList<>(wanted)));
        Files.writeString(lockFile, Json.write(lock));

        // Mods that must be downloaded by hand: skip the ones already dropped into mods/.
        List<String> jars = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(modsDir, "*.jar")) { for (Path p : ds) jars.add(p.getFileName().toString().toLowerCase()); }
        List<Map<String, Object>> missing = new ArrayList<>();
        for (Map<String, Object> m : manual) {
            boolean present = false;
            for (String pat : String.valueOf(m.getOrDefault("match", "")).toLowerCase().split("\\|"))
                if (!pat.isBlank()) for (String j : jars) if (j.contains(pat.trim()) && !wanted.contains(j)) present = true;
            if (present) continue;
            missing.add(m);
            report.add("MANUAL DOWNLOAD (not on Modrinth): " + m.get("name") + " -> " + cfUrl(m)
                    + "  (pick the newest " + mcVersion + " Forge file, put it in the mods folder)");
        }
        log("Resolved " + resolved.size() + " mods (incl. dependencies). " + report.size() + " notice(s).");
        if (!missing.isEmpty()) askManual(missing);
    }

    static String cfUrl(Map<String, Object> m) {
        return "https://www.curseforge.com/minecraft/mc-mods/" + m.get("curseforge") + "/files/all?version=" + mcVersion;
    }

    // Shows a dialog listing mods that need a manual download. "Stop launch" exits with code 1 so Prism cancels the launch.
    static void askManual(List<Map<String, Object>> missing) throws Exception {
        StringBuilder html = new StringBuilder("<html><body style='font-family:sans-serif'><h2>Terrestrial Tribulations: manual downloads</h2>"
                + "<p>Download the newest <b>" + mcVersion + " Forge</b> file of each mod and drop it into:<br><code>" + modsDir + "</code></p><ul>");
        for (Map<String, Object> m : missing) html.append("<li><a href='").append(cfUrl(m)).append("'>").append(m.get("name")).append("</a></li>");
        Path page = syncDir.resolve("MANUAL_DOWNLOADS.html");
        Files.writeString(page, html.append("</ul></body></html>").toString());
        log("Some mods need a manual download, see " + page);
        if (java.awt.GraphicsEnvironment.isHeadless()) return;
        StringBuilder msg = new StringBuilder("These mods are not on Modrinth and must be downloaded by hand\n(newest " + mcVersion + " Forge file, into the instance's mods folder):\n\n");
        for (Map<String, Object> m : missing) msg.append("  - ").append(m.get("name")).append('\n');
        Object[] opts = {"Open download pages + stop launch", "Launch anyway"};
        int c = javax.swing.JOptionPane.showOptionDialog(null, msg.toString(), "Terrestrial Tribulations - ModSync",
                javax.swing.JOptionPane.DEFAULT_OPTION, javax.swing.JOptionPane.WARNING_MESSAGE, null, opts, opts[0]);
        if (c == 0) {
            try {
                java.awt.Desktop d = java.awt.Desktop.getDesktop();
                d.browse(page.toUri());
                d.open(modsDir.toFile());
            } catch (Exception e) { log("Could not open browser: " + e); }
            writeReport();
            System.exit(1);
        }
    }

    static Map<String, Object> lockedOrFetch(Map<String, Object> lock, String key, String pinned) throws Exception {
        Object l = lock.get(key);
        if (l != null) {
            Map<String, Object> lv = obj(l);
            if (pinned == null || pinned.equals(lv.get("version_number"))) return lv;
        }
        String q = "?loaders=" + enc("[\"" + loader + "\"]") + "&game_versions=" + enc("[\"" + mcVersion + "\"]");
        HttpResponse<String> r = HTTP.send(HttpRequest.newBuilder(URI.create(API + "/project/" + enc(key) + "/version" + q))
                .header("User-Agent", UA).timeout(Duration.ofSeconds(60)).build(), HttpResponse.BodyHandlers.ofString());
        if (r.statusCode() == 429) { Thread.sleep(5000); return lockedOrFetch(lock, key, pinned); }
        if (r.statusCode() != 200) return null;
        List<Object> versions = list(Json.parse(r.body()));
        Map<String, Object> pick = null;
        for (Object o : versions) { // newest first; prefer a pinned version, else newest release, else newest anything
            Map<String, Object> v = obj(o);
            if (pinned != null) { if (pinned.equals(v.get("version_number"))) { pick = v; break; } continue; }
            if ("release".equals(v.get("version_type"))) { pick = v; break; }
            if (pick == null) pick = v;
        }
        if (pick == null && pinned != null) {
            report.add("Pinned version " + pinned + " not found for " + key + "; using newest instead.");
            return lockedOrFetch(lock, key, null);
        }
        if (pick == null) return null;
        Map<String, Object> file = null;
        for (Object f : list(pick.get("files"))) { Map<String, Object> fm = obj(f); if (file == null || Boolean.TRUE.equals(fm.get("primary"))) file = fm; }
        if (file == null) return null;
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("project_id", pick.get("project_id"));
        out.put("version_id", pick.get("id"));
        out.put("version_number", pick.get("version_number"));
        out.put("filename", file.get("filename"));
        out.put("url", file.get("url"));
        out.put("sha1", obj(file.get("hashes")).get("sha1"));
        List<Object> deps = new ArrayList<>();
        for (Object d : list(pick.get("dependencies"))) {
            Map<String, Object> dm = obj(d), keep = new LinkedHashMap<>();
            keep.put("project_id", dm.get("project_id"));
            keep.put("dependency_type", dm.get("dependency_type"));
            deps.add(keep);
        }
        out.put("dependencies", deps);
        return out;
    }

    static String readStage() {
        try { String s = Files.readString(syncDir.resolve("stage.txt")).trim().toUpperCase(); return s.isEmpty() ? "C" : s.substring(0, 1); }
        catch (IOException e) { return "C"; }
    }

    static String sha1(Path p) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        try (InputStream in = Files.newInputStream(p)) { byte[] b = new byte[65536]; int n; while ((n = in.read(b)) > 0) md.update(b, 0, n); }
        StringBuilder sb = new StringBuilder(); for (byte x : md.digest()) sb.append(String.format("%02x", x)); return sb.toString();
    }

    static void writeReport() {
        try {
            if (syncDir == null) return;
            StringBuilder sb = new StringBuilder("Terrestrial Tribulations ModSync report\n");
            if (report.isEmpty()) sb.append("All mods resolved and installed.\n");
            for (String s : report) sb.append("- ").append(s).append('\n');
            Files.writeString(syncDir.resolve("sync-report.txt"), sb.toString());
            for (String s : report) log("NOTICE: " + s);
        } catch (IOException ignored) {}
    }

    static void log(String s) { System.out.println("[TT ModSync] " + s); }
    static String enc(String s) { return URLEncoder.encode(s, StandardCharsets.UTF_8); }
    @SuppressWarnings("unchecked") static Map<String, Object> obj(Object o) { return o instanceof Map ? (Map<String, Object>) o : new LinkedHashMap<>(); }
    @SuppressWarnings("unchecked") static List<Object> list(Object o) { return o instanceof List ? (List<Object>) o : new ArrayList<>(); }
    static String str(Object o) { return o == null ? null : o.toString(); }

    // Minimal JSON reader/writer (the JDK has none built in).
    static final class Json {
        final String s; int i;
        Json(String s) { this.s = s; }
        static Object parse(String s) { Json j = new Json(s); j.ws(); Object v = j.val(); return v; }
        void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
        Object val() {
            ws(); char c = s.charAt(i);
            if (c == '{') { i++; Map<String, Object> m = new LinkedHashMap<>(); ws(); if (s.charAt(i) == '}') { i++; return m; }
                while (true) { ws(); String k = strv(); ws(); i++; m.put(k, val()); ws(); char d = s.charAt(i++); if (d == '}') return m; } }
            if (c == '[') { i++; List<Object> l = new ArrayList<>(); ws(); if (s.charAt(i) == ']') { i++; return l; }
                while (true) { l.add(val()); ws(); char d = s.charAt(i++); if (d == ']') return l; } }
            if (c == '"') return strv();
            if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
            if (s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
            if (s.startsWith("null", i)) { i += 4; return null; }
            int st = i; while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
            return Double.parseDouble(s.substring(st, i));
        }
        String strv() {
            StringBuilder b = new StringBuilder(); i++;
            while (true) { char c = s.charAt(i++);
                if (c == '"') return b.toString();
                if (c == '\\') { char e = s.charAt(i++);
                    switch (e) { case 'n' -> b.append('\n'); case 't' -> b.append('\t'); case 'r' -> b.append('\r'); case 'b' -> b.append('\b'); case 'f' -> b.append('\f');
                        case 'u' -> { b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; } default -> b.append(e); } }
                else b.append(c); }
        }
        static String write(Object o) { StringBuilder b = new StringBuilder(); w(o, b, 0); return b.append('\n').toString(); }
        static void w(Object o, StringBuilder b, int ind) {
            String pad = "  ".repeat(ind + 1), end = "  ".repeat(ind);
            if (o instanceof Map<?, ?> m) { if (m.isEmpty()) { b.append("{}"); return; } b.append("{\n"); int n = 0;
                for (Map.Entry<?, ?> e : m.entrySet()) { b.append(pad); w(String.valueOf(e.getKey()), b, ind + 1); b.append(": "); w(e.getValue(), b, ind + 1); if (++n < m.size()) b.append(','); b.append('\n'); }
                b.append(end).append('}'); }
            else if (o instanceof List<?> l) { if (l.isEmpty()) { b.append("[]"); return; } b.append("[\n"); int n = 0;
                for (Object x : l) { b.append(pad); w(x, b, ind + 1); if (++n < l.size()) b.append(','); b.append('\n'); } b.append(end).append(']'); }
            else if (o instanceof String str) { b.append('"'); for (char c : str.toCharArray()) { switch (c) { case '"' -> b.append("\\\""); case '\\' -> b.append("\\\\"); case '\n' -> b.append("\\n"); case '\r' -> b.append("\\r"); case '\t' -> b.append("\\t"); default -> { if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c); } } } b.append('"'); }
            else if (o instanceof Double d && d == Math.floor(d) && !d.isInfinite()) b.append(d.longValue());
            else b.append(o);
        }
    }
}
