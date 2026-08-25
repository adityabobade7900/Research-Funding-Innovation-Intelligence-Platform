import { describe, it, expect } from "vitest";
import { formatRoleName } from "./utils";

describe("formatRoleName", () => {
  it("formats known roles into human-readable titles", () => {
    expect(formatRoleName("researcher")).toBe("Researcher");
    expect(formatRoleName("startup_founder")).toBe("Startup Founder");
    expect(formatRoleName("innovation_manager")).toBe("Innovation Manager");
    expect(formatRoleName("administrator")).toBe("Administrator");
  });

  it("returns unknown roles as-is", () => {
    expect(formatRoleName("guest")).toBe("guest");
  });
});
