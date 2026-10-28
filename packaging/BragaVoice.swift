import AppKit
import Foundation
import WebKit

@main
@MainActor
final class BragaVoiceApp: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKDownloadDelegate {
    private let endpoint = URL(string: "http://127.0.0.1:8765/")!
    private var backendProcess: Process?
    private var window: NSWindow!
    private var webView: WKWebView!
    private var retryCount = 0
    private var downloadDestinations: [ObjectIdentifier: URL] = [:]

    static func main() {
        let application = NSApplication.shared
        let delegate = BragaVoiceApp()
        application.delegate = delegate
        application.setActivationPolicy(.regular)
        application.run()
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        buildMenu()
        buildWindow()
        showLaunchScreen()
        launchBackend()
        loadInterface(after: 0.45)
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    func applicationWillTerminate(_ notification: Notification) {
        guard let process = backendProcess, process.isRunning else { return }
        process.terminate()
    }

    private func buildWindow() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.preferences.isElementFullscreenEnabled = true

        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self
        webView.allowsMagnification = true
        webView.setValue(false, forKey: "drawsBackground")

        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1440, height: 900),
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.title = "BRAGA VOICE"
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true
        window.isMovableByWindowBackground = true
        window.minSize = NSSize(width: 1080, height: 680)
        window.backgroundColor = NSColor(red: 0.025, green: 0.035, blue: 0.075, alpha: 1)
        window.contentView = webView
        window.center()
        window.makeKeyAndOrderFront(nil)
    }

    private func buildMenu() {
        let mainMenu = NSMenu()

        let appItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "Sobre o BRAGA VOICE", action: #selector(showAbout), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Abrir pasta de áudios", action: #selector(openAudioFolder), keyEquivalent: "o")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Encerrar BRAGA VOICE", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu
        mainMenu.addItem(appItem)

        let viewItem = NSMenuItem()
        let viewMenu = NSMenu(title: "Visualizar")
        viewMenu.addItem(withTitle: "Recarregar", action: #selector(reloadInterface), keyEquivalent: "r")
        viewMenu.addItem(withTitle: "Tela cheia", action: #selector(NSWindow.toggleFullScreen(_:)), keyEquivalent: "f")
        viewItem.submenu = viewMenu
        mainMenu.addItem(viewItem)

        NSApp.mainMenu = mainMenu
    }

    private func showLaunchScreen() {
        let html = """
        <!doctype html><html><head><meta charset="utf-8"><style>
        html,body{height:100%;margin:0;background:#060916;color:#dff8ff;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
        body{display:grid;place-items:center;overflow:hidden}.core{width:112px;height:112px;border-radius:50%;border:1px solid #50e6ff;box-shadow:0 0 60px #1598ff88,inset 0 0 35px #67edff55;display:grid;place-items:center;animation:p 1.4s ease-in-out infinite}.core:after{content:'B';font-size:54px;font-weight:700;color:#8cf5ff;text-shadow:0 0 20px #32cfff}.label{margin-top:28px;letter-spacing:.32em;font-size:13px;color:#8facc4;text-align:center}.sub{margin-top:10px;font-size:11px;letter-spacing:.18em;color:#416078;text-align:center}@keyframes p{50%{transform:scale(1.05);box-shadow:0 0 90px #1598ffaa,inset 0 0 45px #67edff77}}
        </style></head><body><main><div class="core"></div><div class="label">BRAGA VOICE</div><div class="sub">INICIALIZANDO NÚCLEO NEURAL</div></main></body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    private func launchBackend() {
        guard let resourceURL = Bundle.main.resourceURL else { return }
        let executable = resourceURL.appendingPathComponent("backend/braga-voice-backend/braga-voice-backend")
        guard FileManager.default.isExecutableFile(atPath: executable.path) else {
            showFatalError("O núcleo de voz não foi encontrado no aplicativo.")
            return
        }

        let supportDirectory = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/BRAGA VOICE", isDirectory: true)
        let logsDirectory = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs/BRAGA VOICE", isDirectory: true)
        try? FileManager.default.createDirectory(at: supportDirectory, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: logsDirectory, withIntermediateDirectories: true)

        let logURL = logsDirectory.appendingPathComponent("backend.log")
        if !FileManager.default.fileExists(atPath: logURL.path) {
            FileManager.default.createFile(atPath: logURL.path, contents: nil)
        }

        let process = Process()
        process.executableURL = executable
        var environment = ProcessInfo.processInfo.environment
        environment["BRAGA_VOICE_ENV_FILE"] = supportDirectory.appendingPathComponent(".env").path
        environment["BRAGA_VOICE_DATA_DIR"] = supportDirectory.path
        environment["BRAGA_VOICE_HOST"] = "127.0.0.1"
        environment["BRAGA_VOICE_PORT"] = "8765"
        process.environment = environment

        if let log = try? FileHandle(forWritingTo: logURL) {
            _ = try? log.seekToEnd()
            process.standardOutput = log
            process.standardError = log
        }

        do {
            try process.run()
            backendProcess = process
        } catch {
            showFatalError("Não foi possível iniciar o núcleo de voz: \(error.localizedDescription)")
        }
    }

    private func loadInterface(after delay: TimeInterval) {
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            guard let self else { return }
            self.webView.load(URLRequest(url: self.endpoint, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 2))
        }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        retryCount = 0
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        retryCount += 1
        if retryCount <= 24 {
            loadInterface(after: 0.5)
        } else {
            showFatalError("O núcleo local não respondeu. Consulte ~/Library/Logs/BRAGA VOICE/backend.log.")
        }
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationAction: WKNavigationAction,
        decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
    ) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.cancel)
            return
        }
        if navigationAction.shouldPerformDownload && url.host == "127.0.0.1" {
            decisionHandler(.download)
        } else if url.host == "127.0.0.1" || url.scheme == "about" {
            decisionHandler(.allow)
        } else {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
        }
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationResponse: WKNavigationResponse,
        decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void
    ) {
        let response = navigationResponse.response as? HTTPURLResponse
        let disposition = response?.value(forHTTPHeaderField: "Content-Disposition") ?? ""
        if disposition.lowercased().contains("attachment") {
            decisionHandler(.download)
        } else {
            decisionHandler(.allow)
        }
    }

    func webView(
        _ webView: WKWebView,
        navigationAction: WKNavigationAction,
        didBecome download: WKDownload
    ) {
        download.delegate = self
    }

    func webView(
        _ webView: WKWebView,
        navigationResponse: WKNavigationResponse,
        didBecome download: WKDownload
    ) {
        download.delegate = self
    }

    func download(
        _ download: WKDownload,
        decideDestinationUsing response: URLResponse,
        suggestedFilename: String,
        completionHandler: @escaping (URL?) -> Void
    ) {
        guard let downloadsDirectory = FileManager.default.urls(
            for: .downloadsDirectory,
            in: .userDomainMask
        ).first else {
            completionHandler(nil)
            return
        }

        let destination = uniqueDownloadURL(
            directory: downloadsDirectory,
            suggestedFilename: suggestedFilename
        )
        downloadDestinations[ObjectIdentifier(download)] = destination
        completionHandler(destination)
    }

    func downloadDidFinish(_ download: WKDownload) {
        guard let destination = downloadDestinations.removeValue(
            forKey: ObjectIdentifier(download)
        ) else { return }
        NSWorkspace.shared.activateFileViewerSelecting([destination])
    }

    func download(
        _ download: WKDownload,
        didFailWithError error: Error,
        resumeData: Data?
    ) {
        downloadDestinations.removeValue(forKey: ObjectIdentifier(download))
        showDownloadError(error.localizedDescription)
    }

    private func uniqueDownloadURL(directory: URL, suggestedFilename: String) -> URL {
        let filename = suggestedFilename.isEmpty ? "braga-voice.mp3" : suggestedFilename
        let original = directory.appendingPathComponent(filename)
        guard FileManager.default.fileExists(atPath: original.path) else { return original }

        let stem = original.deletingPathExtension().lastPathComponent
        let fileExtension = original.pathExtension
        var counter = 2
        while true {
            let candidateName = fileExtension.isEmpty
                ? "\(stem)-\(counter)"
                : "\(stem)-\(counter).\(fileExtension)"
            let candidate = directory.appendingPathComponent(candidateName)
            if !FileManager.default.fileExists(atPath: candidate.path) {
                return candidate
            }
            counter += 1
        }
    }

    private func showDownloadError(_ detail: String) {
        let alert = NSAlert()
        alert.messageText = "Não foi possível baixar o MP3"
        alert.informativeText = detail
        alert.alertStyle = .warning
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    @objc private func reloadInterface() {
        webView.load(URLRequest(url: endpoint, cachePolicy: .reloadIgnoringLocalCacheData))
    }

    @objc private func openAudioFolder() {
        let folder = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/BRAGA VOICE/audio", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        NSWorkspace.shared.open(folder)
    }

    @objc private func showAbout() {
        let alert = NSAlert()
        alert.messageText = "BRAGA VOICE"
        alert.informativeText = "Central de voz com IA para macOS\nElevenLabs Neural Engine · Núcleo local seguro"
        alert.alertStyle = .informational
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    private func showFatalError(_ message: String) {
        let escaped = message
            .replacingOccurrences(of: "&", with: "&amp;")
            .replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")
        let html = """
        <!doctype html><html><body style="margin:0;background:#070915;color:#eef8ff;font-family:-apple-system;display:grid;place-items:center;height:100vh"><main style="max-width:620px;padding:44px;text-align:center"><h1 style="color:#ff6b9e">NÚCLEO INDISPONÍVEL</h1><p style="line-height:1.6;color:#9fb3c8">\(escaped)</p></main></body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }
}
