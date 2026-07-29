export interface InventoryItem {
  id: string;
  name: string;
  category: 'Staples' | 'Vegetables' | 'Fruits' | 'Dairy' | 'Snacks' | 'Beverages' | 'Cleaning' | 'Personal Care' | 'Other';
  quantity: number;
  unit: string;
  status: 'Sufficient' | 'Moderate' | 'Low Stock';
  expectedRemainingDays: number;
  purchaseDate: string;
  expiryDate: string;
  averageWeeklyConsumption: number;
  aiConfidence: number;
  predictedRemainingDays: number;
  recommendation?: string;
}
