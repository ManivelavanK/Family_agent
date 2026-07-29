export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  toolsUsed?: string[];
  steps?: string[];
}

// In-memory session messages
export const chatHistory: ChatMessage[] = [
  {
    id: 'init-1',
    sender: 'agent',
    text: "Hello! I'm Baby Care Agent for KinNest. I can help you understand Aarav's health, predict feeding schedules, analyze sleep patterns, and provide AI-powered parenting guidance. How can I help you today?",
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    toolsUsed: [],
    steps: [],
  },
];

const LATENCY = 2000;

export const aiService = {
  async getMessages(): Promise<ChatMessage[]> {
    return [...chatHistory];
  },

  async sendMessage(text: string): Promise<ChatMessage> {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}-user`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    chatHistory.push(userMsg);

    return new Promise((resolve) => {
      setTimeout(() => {
        let replyText = "I've reviewed your question. Could you provide more details about what you'd like to know about Aarav?";
        let toolsUsed = ['Baby Profile'];
        let steps = ['🧠 Understanding question', '👶 Checking baby profile'];

        const lower = text.toLowerCase();

        if (lower.includes('sleep') || lower.includes('not sleeping') || lower.includes('waking')) {
          replyText = `Based on Aarav's sleep data, there are several possible reasons for disrupted sleep at 10 months:

**1. Sleep Regression (9–10 Month)**
This is very common. Aarav's brain is going through massive developmental leaps — crawling, standing, and language development all happening simultaneously.

**2. Hunger (Growth Spurt)**
With 8 feedings over the past 2 days, Aarav may be in a growth spurt. Consider a small formula top-up before bed.

**3. Environmental Temperature**
Ensure room temperature is between 22–24°C. Aarav's sleep logs show better quality when evening feed is at 9:30 PM.

**4. Teething Discomfort**
At 10 months, molars often begin. Check for gum inflammation.

**Recommendation:** Maintain a consistent bedtime routine — feed at 9:30 PM, dim lights, white noise for 15 mins. Expect improvement within 3–5 days.`;
          toolsUsed = ['Sleep Analysis', 'Feeding Analysis', 'Growth Monitoring', 'Health History'];
          steps = [
            '🧠 Understanding question: sleep disruption at 10 months',
            '😴 Checking sleep logs: reviewed last 7 days of sleep data',
            '🍼 Checking feeding patterns: analyzed feeding frequency and timing',
            '📈 Checking growth data: confirming active growth spurt phase',
            '🩺 Checking health logs: no fever or illness logged',
            '✨ Generating parenting advice: synthesized multi-factor analysis',
          ];
        } else if (lower.includes('feed') || lower.includes('feeding') || lower.includes('milk') || lower.includes('solid')) {
          replyText = `Aarav's feeding analysis looks healthy! Here's a detailed breakdown:

**Current Pattern**
- Average feeding interval: 3.5 hours
- Today's feedings: 8 (on track for age)
- Hydration status: Normal

**AI Prediction**
Next feeding is predicted at **1:30 PM** with 94% confidence based on today's morning formula intake pattern.

**Solid Food Readiness**
At 10 months, Aarav is ready for mashed foods, soft finger foods, and iron-rich foods. Ragi porridge (as logged) is excellent.

**Recommendation:** Continue current feeding schedule. Add 1 serving of protein (dal/egg yolk) at lunch for optimal brain development.`;
          toolsUsed = ['Feeding Analysis', 'Nutrition Monitoring', 'Growth Monitoring'];
          steps = [
            '🧠 Understanding question: feeding patterns and schedule',
            '🍼 Checking feeding logs: analyzed last 48 hours of feeds',
            '📈 Running feeding prediction: calculating next predicted feed time',
            '🥗 Checking nutrition balance: reviewing solid food introduction',
            '✨ Generating feeding recommendation',
          ];
        } else if (lower.includes('vaccin') || lower.includes('vaccine') || lower.includes('immuniz')) {
          replyText = `Aarav's vaccination schedule is almost up to date!

**Upcoming Vaccination (Due in 5 Days)**
- **Measles 1st Dose / MR** — Due at Little Hearts Clinic
- Doctor: Dr. Priya
- Recommended to schedule appointment within next 3 days

**Also Upcoming**
- JE 1st Dose — Due in approximately 25 days

**Completed**
- OPV 3 & Pentavalent 3 ✓
- IPV 2 ✓

**Preparation Tips**
- Feed Aarav 1 hour before vaccination
- Carry immunization card
- Expect mild fever for 24–48 hours post-vaccination

I've set an urgent reminder for the MR vaccine appointment.`;
          toolsUsed = ['Vaccination Schedule', 'Health History', 'Appointment Manager'];
          steps = [
            '🧠 Understanding question: vaccination status',
            '💉 Checking vaccination records: found 2 upcoming vaccines',
            '📅 Checking appointment schedule: no appointment booked yet',
            '🩺 Reviewing health history: no contraindications found',
            '✨ Generating vaccination guidance',
          ];
        } else if (lower.includes('grow') || lower.includes('weight') || lower.includes('height')) {
          replyText = `Aarav's growth is progressing beautifully!

**Current Measurements**
- Weight: **8.4 kg** (50th WHO percentile — excellent!)
- Height: **72.5 cm** (50th WHO percentile — on track!)
- Head Circumference: **45.2 cm** (normal range)

**Monthly Growth**
- Weight gain this month: +0.3 kg (within healthy 0.2–0.5 kg range)

**WHO Comparison**
Aarav is tracking perfectly along the 50th percentile curve, meaning he is exactly at the median for healthy Indian baby boys his age.

**Recommendation:** Continue current diet. Introduce iron-rich cereals and protein to support brain development during this critical period.`;
          toolsUsed = ['Growth Monitoring', 'WHO Standards Database', 'Nutrition Analysis'];
          steps = [
            '🧠 Understanding question: growth tracking',
            '📈 Fetching growth data: retrieved last 6 months of measurements',
            '📊 Comparing against WHO percentile curves',
            '🥗 Cross-referencing with feeding and nutrition logs',
            '✨ Generating growth assessment',
          ];
        } else if (lower.includes('hello') || lower.includes('hi') || lower.includes('help')) {
          replyText = `Hello! I'm KinNest's Baby Care Agent — your AI childcare decision-support system.

I can help you with:
- 😴 **Sleep analysis** and improving Aarav's sleep patterns
- 🍼 **Feeding schedules** and nutrition guidance
- 📈 **Growth monitoring** and WHO percentile tracking
- 💉 **Vaccination reminders** and preparation tips
- 🩺 **Health insights** and symptom guidance
- 🚨 **Emergency guidance** for urgent situations

What would you like to know about Aarav today?`;
          toolsUsed = ['Baby Profile'];
          steps = ['🧠 Processed greeting', '👶 Loaded baby context'];
        }

        const agentMsg: ChatMessage = {
          id: `msg-${Date.now()}-agent`,
          sender: 'agent',
          text: replyText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          toolsUsed,
          steps,
        };
        chatHistory.push(agentMsg);
        resolve(agentMsg);
      }, LATENCY);
    });
  },

  async getDashboardInsight(): Promise<string> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve("Aarav slept well last night for 8.5 hours. His feeding schedule is on track with 8 feeds today. Vaccination (Measles / MR) is due in 5 days — schedule an appointment with Dr. Priya soon. Weight gain remains healthy at the 50th WHO percentile.");
      }, 800);
    });
  },

  async getAlerts() {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.alerts]), 600);
    });
  },
};

// circular import workaround
import { db } from '../data/mockData';
