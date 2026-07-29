export interface FamilyMember {
  name: string;
  role: 'Mother' | 'Father' | 'Grandparent' | 'Guardian';
  phone?: string;
  isEmergencyContact?: boolean;
}

export interface FamilyContext {
  id: string;
  name: string; // e.g. "Arunachalam Family"
  members: FamilyMember[];
}
