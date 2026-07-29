import { ShoppingItem } from '../types/shopping';
import { db } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from './api';

const LATENCY = 600;

export interface AISmartListResponse {
  items: Omit<ShoppingItem, 'id' | 'checked'>[];
  estimatedTotal: number;
}

export const shoppingService = {
  async getShoppingList(): Promise<ShoppingItem[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([...db.shoppingList]);
        }, LATENCY);
      });
    }
    const response = await apiClient.get<any[]>('/shopping/list');
    return response.data.map((item, idx) => ({
      id: `shop-${idx}`,
      name: item.item,
      quantity: item.recommended_purchase,
      unit: item.unit,
      category: item.item.includes('Rice') || item.item.includes('Atta') || item.item.includes('Oil') ? 'Staples' : item.item.includes('Milk') || item.item.includes('Curd') || item.item.includes('Eggs') ? 'Dairy' : 'Vegetables',
      estimatedPrice: item.item.includes('Rice') ? 60 * item.recommended_purchase : item.item.includes('Atta') ? 45 * item.recommended_purchase : 50 * item.recommended_purchase,
      priority: item.recommended_purchase >= 5 ? 'Must Buy' : 'Consider Buying',
      checked: false,
      aiReason: item.reason
    }));
  },

  async addShoppingItem(item: Omit<ShoppingItem, 'id'>): Promise<ShoppingItem> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const newItem: ShoppingItem = {
            ...item,
            id: `shop-${Date.now()}`
          };
          db.shoppingList.push(newItem);
          resolve(newItem);
        }, LATENCY);
      });
    }
    // FastAPI does not have a persistent shopping list table. We manage added items locally in the UI state.
    const newItem: ShoppingItem = {
      ...item,
      id: `shop-${Date.now()}`
    };
    return newItem;
  },

  async updateShoppingItem(id: string, updates: Partial<ShoppingItem>): Promise<ShoppingItem> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = db.shoppingList.findIndex(item => item.id === id);
          if (index === -1) {
            reject(new Error('Shopping item not found'));
            return;
          }
          const updated = {
            ...db.shoppingList[index],
            ...updates
          };
          db.shoppingList[index] = updated;
          resolve(updated);
        }, LATENCY);
      });
    }
    // Managed in UI local state
    return {
      id,
      name: '',
      quantity: 0,
      unit: '',
      category: '',
      checked: false,
      priority: 'Consider Buying',
      estimatedPrice: updates.estimatedPrice !== undefined ? updates.estimatedPrice : 0,
      ...updates
    } as ShoppingItem;
  },

  async deleteShoppingItem(id: string): Promise<boolean> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          db.shoppingList = db.shoppingList.filter(item => item.id !== id);
          resolve(true);
        }, LATENCY);
      });
    }
    // Managed in UI local state
    return true;
  },

  async generateShoppingList(): Promise<AISmartListResponse> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Generate recommendations based on current inventory statuses
          const items: Omit<ShoppingItem, 'id' | 'checked'>[] = [
            {
              name: 'Sona Masoori Rice',
              quantity: 5,
              unit: 'kg',
              category: 'Staples',
              estimatedPrice: 325,
              priority: 'Must Buy',
              aiReason: 'Low inventory. Running out in 4 days.'
            },
            {
              name: 'Organic Milk',
              quantity: 2,
              unit: 'L',
              category: 'Dairy',
              estimatedPrice: 120,
              priority: 'Must Buy',
              aiReason: 'High consumption. Running out today.'
            },
            {
              name: 'Tomatoes',
              quantity: 1,
              unit: 'kg',
              category: 'Vegetables',
              estimatedPrice: 60,
              priority: 'Must Buy',
              aiReason: 'Required for weekly meal plans.'
            },
            {
              name: 'Onions',
              quantity: 2,
              unit: 'kg',
              category: 'Vegetables',
              estimatedPrice: 70,
              priority: 'Must Buy',
              aiReason: 'High daily household usage rate.'
            }
          ];

          resolve({
            items,
            estimatedTotal: 575 // Sum of estimated prices
          });
        }, 1500); // Higher latency for "thinking" animation
      });
    }
    const items = await this.getShoppingList();
    const estimatedTotal = items.reduce((sum, item) => sum + (item.estimatedPrice || 0), 0);
    return {
      items: items.map(item => ({
        name: item.name,
        quantity: item.quantity,
        unit: item.unit,
        category: item.category,
        estimatedPrice: item.estimatedPrice,
        priority: item.priority,
        aiReason: item.aiReason
      })),
      estimatedTotal
    };
  },

  async addAllToShoppingList(items: Omit<ShoppingItem, 'id' | 'checked'>[]): Promise<ShoppingItem[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const addedItems: ShoppingItem[] = items.map((item, idx) => {
            // Check if item already exists in shopping list
            const existingIndex = db.shoppingList.findIndex(si => si.name.toLowerCase() === item.name.toLowerCase());
            
            if (existingIndex !== -1) {
              // Update quantity
              db.shoppingList[existingIndex].quantity += item.quantity;
              db.shoppingList[existingIndex].priority = item.priority;
              db.shoppingList[existingIndex].checked = false; // reset check
              return db.shoppingList[existingIndex];
            } else {
              const newItem: ShoppingItem = {
                ...item,
                id: `shop-${Date.now()}-${idx}`,
                checked: false
              };
              db.shoppingList.push(newItem);
              return newItem;
            }
          });
          resolve(addedItems);
        }, LATENCY);
      });
    }
    return items.map((item, idx) => ({
      ...item,
      id: `shop-${Date.now()}-${idx}`,
      checked: false
    }));
  }
};
