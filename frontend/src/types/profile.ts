export interface ResearchDomain {
  id: number;
  name: string;
  description?: string;
}

export interface ResearchInterest {
  id?: number;
  profile_id?: number;
  title: string;
  description?: string;
  importance_level: 'primary' | 'secondary' | 'exploratory' | string;
}

export interface ProfileKeyword {
  id?: number;
  profile_id?: number;
  keyword: string;
}

export interface TechnologyArea {
  id?: number;
  profile_id?: number;
  name: string;
  description?: string;
}

export interface AcademicHistory {
  id?: number;
  profile_id?: number;
  degree: string;
  field_of_study: string;
  institution: string;
  start_year?: number;
  end_year?: number;
}

export interface ResearchHistory {
  id?: number;
  profile_id?: number;
  project_title: string;
  role: string;
  organization: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface ExtendedProfile {
  id: number;
  user_id: number;
  institution?: string;
  department?: string;
  bio?: string;
  orcid_id?: string;
  website?: string;
  created_at: string;
  updated_at: string;
  domains: ResearchDomain[];
  interests: ResearchInterest[];
  keywords: ProfileKeyword[];
  technology_areas: TechnologyArea[];
  academic_histories: AcademicHistory[];
  research_histories: ResearchHistory[];
}

export interface ExtendedProfileUpdate {
  institution?: string;
  department?: string;
  bio?: string;
  orcid_id?: string;
  website?: string;
  domain_ids?: number[];
  interests?: ResearchInterest[];
  keywords?: string[];
  technology_areas?: TechnologyArea[];
  academic_histories?: AcademicHistory[];
  research_histories?: ResearchHistory[];
}
