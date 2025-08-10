import { Router } from "express";
import Stripe from "stripe";
import dotenv from "dotenv";
import { requireEnv } from "./utils/env.js";
dotenv.config();

const router = Router();
const STRIPE_SECRET_KEY = requireEnv("STRIPE_SECRET_KEY");
const STRIPE_WEBHOOK_SECRET = requireEnv("STRIPE_WEBHOOK_SECRET");
const STRIPE_PRICE_PRO = requireEnv("STRIPE_PRICE_PRO");
const SUCCESS_URL = requireEnv("SUCCESS_URL");
const CANCEL_URL = requireEnv("CANCEL_URL");
const stripe = new Stripe(STRIPE_SECRET_KEY, { apiVersion: "2024-06-20" });

// TODO: replace with your DB update
async function grantPlan(customerId: string, plan: "free"|"pro", ageToken?: string){
  console.log("Grant plan:", { customerId, plan, ageToken });
}

router.post("/stripe/webhook", (req, res) => {
  try {
    const sig = req.headers["stripe-signature"] as string;
    const event = stripe.webhooks.constructEvent(
      (req as any).body,
      sig,
      STRIPE_WEBHOOK_SECRET
    );

    switch (event.type) {
      case "checkout.session.completed": {
        const s = event.data.object as Stripe.Checkout.Session;
        const customerId = String(s.customer);
        grantPlan(customerId, "pro");
        break;
      }
      case "identity.verification_session.verified": {
        const v = event.data.object as any;
        const token = `age_${v.id}`;
        const customerId = v.metadata?.stripe_customer_id || "";
        grantPlan(customerId, "pro", token);
        break;
      }
      case "customer.subscription.deleted": {
        const sub = event.data.object as Stripe.Subscription;
        grantPlan(String(sub.customer), "free");
        break;
      }
      default:
        // ignore others
        break;
    }

    res.json({ received: true });
  } catch (err:any) {
    console.error("Webhook error:", err.message);
    res.status(400).send(`Webhook Error: ${err.message}`);
  }
});

// --- CREATE CHECKOUT SESSION ---
router.post("/billing/checkout", async (req, res) => {
  try {
    const { customer_email } = req.body || {};
    const price = STRIPE_PRICE_PRO; // e.g. price_123 from Stripe

    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price, quantity: 1 }],
      // optional: pass through metadata so webhook can map users later
      metadata: { app: "companion_mvp" },
      customer_email, // or use a saved Stripe customer id if you have one
      success_url: `${SUCCESS_URL}?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${CANCEL_URL}`,
      allow_promotion_codes: true
    });

    res.json({ sessionId: session.id, url: session.url });
  } catch (e: any) {
    console.error("checkout error", e.message);
    res.status(500).json({ error: "checkout_failed" });
  }
});

export default router;
