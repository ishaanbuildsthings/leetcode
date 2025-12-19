export interface ITag {
  id: string;
  name: string;
  slug: string;
  description: string | null;
}

export interface IPlatform {
  id: string;
  name: string;
  slug: string;
}

export type ProgrammingLanguage = "Python" | "Cpp" | "JavaScript";

export interface ISolution {
  id: string;
  problemId: string;
  language: ProgrammingLanguage;
  submissionUrl: string | null;
  githubUrl: string | null;
}

export interface IProblem {
  id: string;
  platformId: string;
  platformProblemId: string | null;
  title: string;
  url: string;
  platformDifficulty: string | null;
  normalizedDifficulty: number | null;
  simplifiedStatement: string | null;
  notes: string | null;
  isGreatProblem: boolean;
}

export interface IProblemWithRelations extends IProblem {
  platform: IPlatform;
  tags: Array<{
    tag: ITag;
    role: "core" | "secondary" | "mention" | null;
    tagDifficulty: number | null;
    isInstructive: boolean | null;
  }>;
  solutions: ISolution[];
}

