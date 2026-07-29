import { InventoryItem } from '../types/inventory';
import { db } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from './api';

const LATENCY = 600; // ms simulated network delay

export const inventoryService = {
  async getInventory(): Promise<InventoryItem[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([...db.inventory]);
        }, LATENCY);
      });
    }
    const response = await apiClient.get<any[]>('/inventory/');
    return response.data.map(item => {
      // Set reasonable defaults for weekly consumption based on common benchmarks
      const weeklyCons = item.name.includes('Rice') ? 2.0 : item.name.includes('Atta') ? 3.0 : item.name.includes('Milk') ? 7.0 : 1.0;
      const remainingDays = Math.ceil((item.quantity / weeklyCons) * 7);
      return {
        id: String(item.id),
        name: item.name,
        category: item.category || 'Staples',
        quantity: item.quantity,
        unit: item.unit || 'units',
        status: remainingDays <= 2 ? 'Low Stock' : remainingDays <= 5 ? 'Moderate' : 'Sufficient',
        averageWeeklyConsumption: weeklyCons,
        predictedRemainingDays: remainingDays,
        expectedRemainingDays: remainingDays,
        purchaseDate: '',
        expiryDate: '',
        aiConfidence: 92,
        recommendation: remainingDays <= 4 ? `Add ${Math.ceil(weeklyCons * 1.5)} ${item.unit} to shopping list.` : undefined
      };
    });
  },

  async addInventoryItem(item: Omit<InventoryItem, 'id' | 'status' | 'predictedRemainingDays' | 'expectedRemainingDays' | 'aiConfidence'>): Promise<InventoryItem> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Calculate mock prediction metrics for AI simulation
          const predictedRemainingDays = Math.ceil((item.quantity / (item.averageWeeklyConsumption || 1)) * 7);
          const aiConfidence = 85 + Math.floor(Math.random() * 13); // 85% - 97%
          let status: 'Sufficient' | 'Moderate' | 'Low Stock' = 'Sufficient';
          if (predictedRemainingDays <= 2) {
            status = 'Low Stock';
          } else if (predictedRemainingDays <= 5) {
            status = 'Moderate';
          }

          const newItem: InventoryItem = {
            ...item,
            id: `inv-${Date.now()}`,
            status,
            expectedRemainingDays: predictedRemainingDays,
            predictedRemainingDays,
            aiConfidence,
            recommendation: predictedRemainingDays <= 4 ? `Buy ${Math.ceil(item.averageWeeklyConsumption * 2)} ${item.unit} within the next 2 days.` : undefined
          };

          db.inventory.push(newItem);
          resolve(newItem);
        }, LATENCY);
      });
    }
    const response = await apiClient.post<any>('/inventory/add', {
      name: item.name,
      category: item.category,
      quantity: Number(item.quantity),
      unit: item.unit
    });
    const added = response.data;
    const weeklyCons = item.averageWeeklyConsumption || 1.0;
    const remainingDays = Math.ceil((added.quantity / weeklyCons) * 7);
    return {
      id: String(added.id),
      name: added.name,
      category: added.category,
      quantity: added.quantity,
      unit: added.unit,
      status: remainingDays <= 2 ? 'Low Stock' : remainingDays <= 5 ? 'Moderate' : 'Sufficient',
      averageWeeklyConsumption: weeklyCons,
      predictedRemainingDays: remainingDays,
      expectedRemainingDays: remainingDays,
      purchaseDate: '',
      expiryDate: '',
      aiConfidence: 90
    };
  },

  async updateInventoryItem(id: string, updates: Partial<InventoryItem>): Promise<InventoryItem> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = db.inventory.findIndex(item => item.id === id);
          if (index === -1) {
            reject(new Error('Item not found'));
            return;
          }

          // Re-calculate mock status if quantity or averageWeeklyConsumption is modified
          const currentItem = db.inventory[index];
          const newQty = updates.quantity !== undefined ? updates.quantity : currentItem.quantity;
          const newWeeklyCons = updates.averageWeeklyConsumption !== undefined ? updates.averageWeeklyConsumption : currentItem.averageWeeklyConsumption;
          
          const predictedRemainingDays = Math.ceil((newQty / (newWeeklyCons || 1)) * 7);
          let status: 'Sufficient' | 'Moderate' | 'Low Stock' = 'Sufficient';
          if (predictedRemainingDays <= 2) {
            status = 'Low Stock';
          } else if (predictedRemainingDays <= 5) {
            status = 'Moderate';
          }

          const updatedItem: InventoryItem = {
            ...currentItem,
            ...updates,
            status,
            expectedRemainingDays: predictedRemainingDays,
            predictedRemainingDays,
            recommendation: predictedRemainingDays <= 4 ? `Buy ${Math.ceil(newWeeklyCons * 2)} ${currentItem.unit} within the next 2 days.` : undefined
          };

          db.inventory[index] = updatedItem;
          resolve(updatedItem);
        }, LATENCY);
      });
    }
    // FastAPI does not implement PUT /inventory/{id}, so we update the local/UI state representation.
    const items = await this.getInventory();
    const item = items.find(i => i.id === id);
    if (!item) throw new Error('Item not found');
    return {
      ...item,
      ...updates
    };
  },

  async deleteInventoryItem(id: string): Promise<boolean> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          db.inventory = db.inventory.filter(item => item.id !== id);
          resolve(true);
        }, LATENCY);
      });
    }
    // Look up the item's name by fetching inventory first, since delete expects item_name
    const items = await this.getInventory();
    const item = items.find(i => i.id === id);
    if (item) {
      await apiClient.delete(`/inventory/${item.name}`);
      return true;
    }
    return false;
  },

  async getConsumptionPrediction(id: string): Promise<Partial<InventoryItem>> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const item = db.inventory.find(i => i.id === id);
          if (!item) {
            reject(new Error('Item not found'));
            return;
          }
          resolve({
            name: item.name,
            quantity: item.quantity,
            unit: item.unit,
            averageWeeklyConsumption: item.averageWeeklyConsumption,
            predictedRemainingDays: item.predictedRemainingDays,
            aiConfidence: item.aiConfidence,
            recommendation: item.recommendation
          });
        }, LATENCY);
      });
    }
    const items = await this.getInventory();
    const item = items.find(i => i.id === id);
    if (!item) throw new Error('Item not found');
    const response = await apiClient.get<any>(`/prediction/${item.name}`);
    return {
      name: item.name,
      quantity: item.quantity,
      unit: item.unit,
      averageWeeklyConsumption: Math.round(response.data.predicted_daily_usage * 7 * 10) / 10,
      predictedRemainingDays: response.data.days_remaining,
      aiConfidence: 94,
      recommendation: response.data.recommended_purchase > 0 
        ? `Order ${response.data.recommended_purchase} ${item.unit} immediately.` 
        : undefined
    };
  }
};
