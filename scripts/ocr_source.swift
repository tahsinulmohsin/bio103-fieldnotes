// Optional local OCR supplement. No network or external biology knowledge is used.
// Compile: swiftc ocr_source.swift -o ocr-source
// Usage: ocr-source paths.txt > source-ocr.jsonl
import Foundation
import Vision
import ImageIO

struct Block: Codable { let text: String; let confidence: Float; let x: Double; let y: Double; let width: Double; let height: Double }
struct Result: Codable { let path: String; let text: String; let blocks: [Block]; let error: String? }
let paths = try String(contentsOfFile: CommandLine.arguments[1], encoding: .utf8).split(separator: "\n").map(String.init)
let encoder = JSONEncoder()
encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
for path in paths {
    autoreleasepool {
        var blocks: [Block] = []
        var failure: String? = nil
        do {
            let request = VNRecognizeTextRequest()
            request.recognitionLevel = .accurate
            request.recognitionLanguages = ["en-US"]
            request.usesLanguageCorrection = false
            let handler = VNImageRequestHandler(url: URL(fileURLWithPath: path), options: [:])
            try handler.perform([request])
            blocks = (request.results ?? []).compactMap { observation in
                guard let candidate = observation.topCandidates(1).first else { return nil }
                let b = observation.boundingBox
                return Block(text: candidate.string, confidence: candidate.confidence, x: b.minX, y: b.minY, width: b.width, height: b.height)
            }
        } catch { failure = error.localizedDescription }
        let result = Result(path: path, text: blocks.map(\.text).joined(separator: "\n"), blocks: blocks, error: failure)
        if let data = try? encoder.encode(result), let line = String(data: data, encoding: .utf8) { print(line) }
    }
}
