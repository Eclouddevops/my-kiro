import { describe, expect, it } from "vitest";
import { languageForPath } from "./language";

describe("languageForPath", () => {
  it("maps known extensions", () => {
    expect(languageForPath("src/app.ts")).toBe("typescript");
    expect(languageForPath("main.py")).toBe("python");
    expect(languageForPath("README.md")).toBe("markdown");
    expect(languageForPath("style.css")).toBe("css");
  });

  it("falls back to plaintext for unknown extensions", () => {
    expect(languageForPath("data.bin")).toBe("plaintext");
    expect(languageForPath("Dockerfile")).toBe("plaintext");
  });
});
