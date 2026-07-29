import { InventoryItem } from '../types/inventory';
import { ShoppingItem } from '../types/shopping';
import { MealPlanDay } from '../types/meal';
import { FamilyContext } from '../types/family';
import { Message } from '../types/ai';

export const initialFamilyContext: FamilyContext = {
  name: 'Arunachalam Family',
  members: [
    { name: 'Meenakshi', role: 'Mother' },
    { name: 'Arunachalam', role: 'Father' },
    { name: 'Karthik', role: 'College Student' },
    { name: 'Vidhya', role: 'School Child' },
    { name: 'Kalyani', role: 'Grandmother' },
    { name: 'Ramanathan', role: 'Grandfather' }
  ],
  dietPreference: 'South Indian Vegetarian preferred',
  weeklyBudget: 3000
};

export const initialInventory: InventoryItem[] = [
  {
    id: 'inv-1',
    name: 'Sona Masoori Rice',
    category: 'Staples',
    quantity: 8.5,
    unit: 'kg',
    status: 'Sufficient',
    expectedRemainingDays: 4,
    purchaseDate: '2026-07-25',
    expiryDate: '2027-07-25',
    averageWeeklyConsumption: 2.2,
    aiConfidence: 92,
    predictedRemainingDays: 4,
    recommendation: 'Buy 5 kg within the next 2 days.'
  },
  {
    id: 'inv-2',
    name: 'Ashirvaad Atta',
    category: 'Staples',
    quantity: 4.0,
    unit: 'kg',
    status: 'Sufficient',
    expectedRemainingDays: 10,
    purchaseDate: '2026-07-25',
    expiryDate: '2027-01-25',
    averageWeeklyConsumption: 3.0,
    aiConfidence: 91,
    predictedRemainingDays: 10
  },
  {
    id: 'inv-3',
    name: 'Amul Fresh Milk',
    category: 'Dairy',
    quantity: 0.5,
    unit: 'L',
    status: 'Low Stock',
    expectedRemainingDays: 1,
    purchaseDate: '2026-07-28',
    expiryDate: '2026-07-30',
    averageWeeklyConsumption: 7.2,
    aiConfidence: 96,
    predictedRemainingDays: 1,
    recommendation: 'Buy 2 L today to meet daily family breakfast demand.'
  },
  {
    id: 'inv-4',
    name: 'Tomatoes',
    category: 'Vegetables',
    quantity: 1.2,
    unit: 'kg',
    status: 'Moderate',
    expectedRemainingDays: 3,
    purchaseDate: '2026-07-28',
    expiryDate: '2026-08-04',
    averageWeeklyConsumption: 2.8,
    aiConfidence: 89,
    predictedRemainingDays: 3,
    recommendation: 'Buy 1.5 kg by Friday for weekend sambar.'
  },
  {
    id: 'inv-5',
    name: 'Onions',
    category: 'Vegetables',
    quantity: 1.5,
    unit: 'kg',
    status: 'Moderate',
    expectedRemainingDays: 3,
    purchaseDate: '2026-07-24',
    expiryDate: '2026-08-15',
    averageWeeklyConsumption: 3.2,
    aiConfidence: 88,
    predictedRemainingDays: 3,
    recommendation: 'Buy 2 kg within the next 2 days.'
  },
  {
    id: 'inv-6',
    name: 'Fortune Sunflower Oil',
    category: 'Staples',
    quantity: 2.0,
    unit: 'L',
    status: 'Sufficient',
    expectedRemainingDays: 12,
    purchaseDate: '2026-07-01',
    expiryDate: '2027-01-01',
    averageWeeklyConsumption: 1.2,
    aiConfidence: 94,
    predictedRemainingDays: 12
  },
  {
    id: 'inv-7',
    name: 'Milky Mist Paneer',
    category: 'Dairy',
    quantity: 0.0,
    unit: 'g',
    status: 'Low Stock',
    expectedRemainingDays: 0,
    purchaseDate: '2026-07-22',
    expiryDate: '2026-07-25',
    averageWeeklyConsumption: 0.5,
    aiConfidence: 95,
    predictedRemainingDays: 0,
    recommendation: 'Stock depleted. Reorder paneer for upcoming weekend meals.'
  },
  {
    id: 'inv-8',
    name: 'Free Range Eggs',
    category: 'Dairy',
    quantity: 6,
    unit: 'pcs',
    status: 'Sufficient',
    expectedRemainingDays: 6,
    purchaseDate: '2026-07-15',
    expiryDate: '2026-08-10',
    averageWeeklyConsumption: 6.0,
    aiConfidence: 93,
    predictedRemainingDays: 6
  },
  {
    id: 'inv-9',
    name: 'Spinach',
    category: 'Vegetables',
    quantity: 0.0,
    unit: 'kg',
    status: 'Low Stock',
    expectedRemainingDays: 0,
    purchaseDate: '2026-07-24',
    expiryDate: '2026-07-27',
    averageWeeklyConsumption: 1.0,
    aiConfidence: 85,
    predictedRemainingDays: 0,
    recommendation: 'Spinach is out of stock (and expired). Purchase fresh bunch today.'
  }
];

export const initialShoppingList: ShoppingItem[] = [
  {
    id: 'shop-1',
    name: 'Sona Masoori Rice',
    quantity: 5,
    unit: 'kg',
    category: 'Staples',
    estimatedPrice: 325,
    priority: 'Must Buy',
    aiReason: 'Predicted to run out in 4 days.',
    checked: false
  },
  {
    id: 'shop-2',
    name: 'Organic Milk',
    quantity: 2,
    unit: 'L',
    category: 'Dairy',
    estimatedPrice: 120,
    priority: 'Must Buy',
    aiReason: 'High family consumption, running low.',
    checked: false
  },
  {
    id: 'shop-3',
    name: 'Tomatoes',
    quantity: 1,
    unit: 'kg',
    category: 'Vegetables',
    estimatedPrice: 60,
    priority: 'Must Buy',
    aiReason: 'Required for scheduled Monday lunch Sambar.',
    checked: false
  },
  {
    id: 'shop-4',
    name: 'Marie Gold Biscuits',
    quantity: 3,
    unit: 'packs',
    category: 'Snacks',
    estimatedPrice: 60,
    priority: 'Consider Buying',
    aiReason: 'Snacks low. Grandchildren demand replenishment.',
    checked: false
  },
  {
    id: 'shop-5',
    name: 'Spinach',
    quantity: 1,
    unit: 'bunch',
    category: 'Vegetables',
    estimatedPrice: 30,
    priority: 'Must Buy',
    aiReason: 'Pantry bunch expired.',
    checked: false
  },
  {
    id: 'shop-6',
    name: 'Fortune Sunflower Oil',
    quantity: 2,
    unit: 'L',
    category: 'Staples',
    estimatedPrice: 280,
    priority: 'Already Available',
    aiReason: 'Sufficient inventory (2L remaining).',
    checked: true
  }
];

export const initialMealPlan: MealPlanDay[] = [
  {
    day: 'Monday',
    breakfast: 'Idli + Sambar',
    lunch: 'Rice + Dal + Poriyal',
    dinner: 'Chapati + Kurma',
    ingredientsAvailability: 'Sufficient',
    missingIngredientsCount: 0
  },
  {
    day: 'Tuesday',
    breakfast: 'Pongal + Coconut Chutney',
    lunch: 'Rice + Rasam + Potato Fry',
    dinner: 'Dosa + Sambar',
    ingredientsAvailability: 'Sufficient',
    missingIngredientsCount: 0
  },
  {
    day: 'Wednesday',
    breakfast: 'Rava Upma',
    lunch: 'Sambar Rice + Papad',
    dinner: 'Idiyappam + Coconut Milk',
    ingredientsAvailability: 'Missing',
    missingIngredientsCount: 2
  },
  {
    day: 'Thursday',
    breakfast: 'Puri + Potato Masala',
    lunch: 'Rice + Lemon Soup + Beans Poriyal',
    dinner: 'Adai + Avial',
    ingredientsAvailability: 'Sufficient',
    missingIngredientsCount: 0
  },
  {
    day: 'Friday',
    breakfast: 'Semiya Upma',
    lunch: 'Veg Biryani + Onion Raitha',
    dinner: 'Chapati + Paneer Butter Masala',
    ingredientsAvailability: 'Missing',
    missingIngredientsCount: 3
  },
  {
    day: 'Saturday',
    breakfast: 'Pesarattu + Ginger Chutney',
    lunch: 'Rice + Karakuzhambu + Appalam',
    dinner: 'Dosa + Tomato Thokku',
    ingredientsAvailability: 'Sufficient',
    missingIngredientsCount: 0
  },
  {
    day: 'Sunday',
    breakfast: 'Appam + Vegetable Stew',
    lunch: 'Millet Biryani + Dal Fry + Gobi Manchurian',
    dinner: 'Uthappam + Chutney Trio',
    ingredientsAvailability: 'Sufficient',
    missingIngredientsCount: 0
  }
];

export const purchaseHistory = [
  { id: 'p-1', date: '2026-07-28', store: 'DMart', itemsCount: 12, amount: 1850, category: 'Staples & Dairy' },
  { id: 'p-2', date: '2026-07-23', store: 'Local Vegetable Shop', itemsCount: 8, amount: 620, category: 'Vegetables' },
  { id: 'p-3', date: '2026-07-15', store: 'Nilgiris Grocery Store', itemsCount: 15, amount: 2450, category: 'Staples & Personal Care' },
  { id: 'p-4', date: '2026-07-10', store: 'Local Organic Vendor', itemsCount: 4, amount: 890, category: 'Fruits' },
  { id: 'p-5', date: '2026-07-02', store: 'DMart', itemsCount: 22, amount: 4890, category: 'Mixed Groceries' }
];

export const spendingAnalytics = {
  monthlyData: [
    { month: 'Feb', spending: 8800, budget: 12000 },
    { month: 'Mar', spending: 10400, budget: 12000 },
    { month: 'Apr', spending: 9800, budget: 12000 },
    { month: 'May', spending: 11200, budget: 12000 },
    { month: 'Jun', spending: 10800, budget: 12000 },
    { month: 'Jul', spending: 8450, budget: 12000 }
  ],
  categoryData: [
    { name: 'Staples', value: 3400, color: '#3B82F6' },
    { name: 'Vegetables', value: 1850, color: '#10B981' },
    { name: 'Dairy', value: 1600, color: '#F59E0B' },
    { name: 'Snacks & Beverages', value: 980, color: '#8B5CF6' },
    { name: 'Cleaning & Others', value: 620, color: '#EC4899' }
  ],
  wasteData: {
    purchased: 10200,
    consumed: 9400,
    estimatedWaste: 800,
    insight: 'Tomatoes are frequently purchased in excess. Reducing weekly purchases by approximately 500 g may reduce waste.'
  }
};

export const initialAlerts = [
  {
    id: 'alert-1',
    type: 'critical',
    title: 'Rice may run out soon',
    message: 'Expected depletion in 4 days.',
    actionLabel: 'Add to List',
    actionType: 'add_rice',
    resolved: false
  },
  {
    id: 'alert-2',
    type: 'warning',
    title: 'Milk consumption increased',
    message: 'Family consumption increased 22% this week.',
    actionLabel: 'View Details',
    actionType: 'view_details',
    resolved: false
  },
  {
    id: 'alert-3',
    type: 'warning',
    title: 'Grocery budget warning',
    message: 'You may exceed the monthly grocery budget by approximately ₹900.',
    actionLabel: 'View Budget',
    actionType: 'view_budget',
    resolved: false
  },
  {
    id: 'alert-4',
    type: 'info',
    title: 'Waste reduction opportunity',
    message: 'Planning meals before shopping could reduce estimated waste.',
    actionLabel: 'Create Meal Plan',
    actionType: 'create_meal_plan',
    resolved: false
  }
];

export const initialMessages: Message[] = [
  {
    id: 'm-1',
    sender: 'agent',
    text: 'Hello Meenakshi! I am Mother Agent, your AI household and grocery intelligence assistant. I have reviewed your pantry logs. Sona Masoori Rice may run out in 4 days, vegetables are sufficient for 3 days, and grocery spending is currently 8% below the weekly budget target.',
    timestamp: '10:00 AM'
  }
];

// In-Memory Database Toggles and mutable storage
export const db = {
  familyContext: { ...initialFamilyContext },
  inventory: [...initialInventory],
  shoppingList: [...initialShoppingList],
  mealPlan: [...initialMealPlan],
  alerts: [...initialAlerts],
  messages: [...initialMessages]
};
