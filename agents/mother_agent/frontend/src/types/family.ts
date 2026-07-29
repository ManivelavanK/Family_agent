export interface FamilyMember {
  name: string;
  role: string;
}

export interface FamilyContext {
  name: string;
  members: FamilyMember[];
  dietPreference: string;
  weeklyBudget: number;
}
