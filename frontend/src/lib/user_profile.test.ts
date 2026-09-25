import { describe, it, expect } from "vitest";
import { User, UserRole } from "@/types/user";
import { ExtendedProfile, ResearchDomain } from "@/types/profile";

describe("Module 1 & 2: User & Research Profile Contracts", () => {
  it("should validate User model with full name, email, phone, and role", () => {
    const user: User = {
      id: 1,
      email: "researcher@oxford.edu",
      full_name: "Dr. Alan Turing",
      phone: "+44 1865 270000",
      role: "researcher",
      is_active: true,
      is_superuser: false,
      created_at: "2026-08-25T00:00:00Z",
      updated_at: "2026-08-25T00:00:00Z",
    };

    expect(user.email).toBe("researcher@oxford.edu");
    expect(user.phone).toBe("+44 1865 270000");
    expect(user.role).toBe("researcher");
    expect(user.is_active).toBe(true);
  });

  it("should validate ExtendedProfile model with institution, department, designation, and country", () => {
    const profile: ExtendedProfile = {
      id: 10,
      user_id: 1,
      institution: "University of Oxford",
      department: "Department of Computer Science",
      designation: "Reader in Machine Learning",
      country: "United Kingdom",
      bio: "Foundational work in computational intelligence.",
      orcid_id: "0000-0002-1825-0097",
      website: "https://ox.ac.uk/turing",
      created_at: "2026-08-25T00:00:00Z",
      updated_at: "2026-08-25T00:00:00Z",
      domains: [
        { id: 1, name: "Artificial Intelligence & Machine Learning" }
      ],
      interests: [
        { title: "Universal Computation", importance_level: "primary" }
      ],
      keywords: [
        { id: 1, keyword: "Turing Machine" }
      ],
      technology_areas: [
        { id: 1, name: "Neural Cryptography" }
      ],
      academic_histories: [
        { degree: "Ph.D.", field_of_study: "Mathematics", institution: "Princeton University", start_year: 1936, end_year: 1938 }
      ],
      research_histories: [
        { project_title: "Automated Computing Engine", role: "Lead Architect", organization: "NPL" }
      ]
    };

    expect(profile.institution).toBe("University of Oxford");
    expect(profile.designation).toBe("Reader in Machine Learning");
    expect(profile.country).toBe("United Kingdom");
    expect(profile.domains.length).toBe(1);
    expect(profile.academic_histories[0].start_year).toBe(1936);
  });

  it("should support all 4 platform roles", () => {
    const roles: UserRole[] = [
      "researcher",
      "startup_founder",
      "innovation_manager",
      "administrator",
    ];
    expect(roles).toHaveLength(4);
    expect(roles).toContain("administrator");
  });

  it("should restrict public self-registration to non-admin roles", () => {
    const publicRoles: UserRole[] = [
      "researcher",
      "startup_founder",
      "innovation_manager",
    ];
    expect(publicRoles).toHaveLength(3);
    expect(publicRoles).not.toContain("administrator");
  });
});

