export interface ShoppingItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  category: string;
  estimatedPrice: number;
  priority: 'Must Buy' | 'Consider Buying' | 'Already Available';
  aiReason?: string;
  checked: boolean;
}
