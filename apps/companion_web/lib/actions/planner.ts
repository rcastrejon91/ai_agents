type Step = {
  id: string;
  kind:
    | 'rides.request'
    | 'payments.transfer'
    | 'travel.search'
    | 'travel.book'
    | 'lodging.search'
    | 'lodging.request'
    | 'social.post'
    | 'site.deploy'
    | 'voice.call';
  params: Record<string, any>;
  preview: string;
};
type Plan = { summary: string; steps: Step[]; estimate?: { usd?: number } };

export async function planFromIntent(intent: string, params: Record<string, any>): Promise<Plan> {
  const t = intent.toLowerCase();

  // 1) Rides
  if (/uber|ride|lyft|pick.*up/i.test(t)) {
    const p = {
      pickup: params.pickup ?? 'current_location',
      dropoff: params.dropoff ?? params.destination ?? 'home',
      service: params.service ?? 'standard',
    };
    return {
      summary: `Request a ride ${p.service} from ${p.pickup} to ${p.dropoff}`,
      steps: [
        {
          id: 'ride1',
          kind: 'rides.request',
          params: p,
          preview: `Open ride-hail link for ${p.service}`,
        },
      ],
    };
  }

  // 2) Transfer funds
  if (/transfer|move.*funds|send.*money/i.test(t)) {
    const p = {
      from: params.from ?? 'account_1',
      to: params.to ?? 'account_2',
      amount: params.amount,
      memo: params.memo ?? 'Lyra transfer',
    };
    return {
      summary: `Transfer $${p.amount} from ${p.from} to ${p.to}`,
      steps: [
        {
          id: 'pay1',
          kind: 'payments.transfer',
          params: p,
          preview: `$${p.amount} ${p.from} → ${p.to}`,
        },
      ],
      estimate: { usd: 0 }, // ACH cost near-zero
    };
  }

  // 3) Trip to Mexico + Airbnb
  if (/trip.*mexico|book.*mexico/i.test(t)) {
    const start = params.start ?? 'next Thursday';
    const days = params.days ?? 7;
    const guests = params.guests ?? 9;
    const city = params.city ?? 'Cancún';
    return {
      summary: `Plan ${days} days in ${city}, ${guests} guests, starting ${start}.`,
      steps: [
        {
          id: 'fly1',
          kind: 'travel.search',
          params: { from: params.from ?? 'ORD', to: 'CUN', start, days },
          preview: 'Search roundtrip flights',
        },
        {
          id: 'stay1',
          kind: 'lodging.search',
          params: { city, guests, start, days },
          preview: 'Search lodging for 9 guests',
        },
        {
          id: 'book1',
          kind: 'travel.book',
          params: { hold: true },
          preview: 'Hold best flight with 24h cancellation',
        },
        {
          id: 'stay2',
          kind: 'lodging.request',
          params: { platform: 'preferred', hold: true },
          preview: 'Request Airbnb/alt stay',
        },
      ],
    };
  }

  // 4) Update social profiles
  if (/update.*(facebook|instagram|ig|tiktok)/i.test(t)) {
    return {
      summary: 'Prepare & post updates to connected social accounts',
      steps: [
        {
          id: 'soc1',
          kind: 'social.post',
          params,
          preview: 'Draft + post to FB/IG/TikTok',
        },
      ],
    };
  }

  // 5) Call a store and place order
  if (/call.*store|place.*order/i.test(t)) {
    const p = { phone: params.phone, script: params.script, order: params.order };
    return {
      summary: `Place a phone order with the store`,
      steps: [
        {
          id: 'call1',
          kind: 'voice.call',
          params: p,
          preview: `Call ${p.phone || 'the store'} and read script`,
        },
      ],
    };
  }

  // 6) Setup website
  if (/setup.*website|create.*site|deploy.*site/i.test(t)) {
    return {
      summary: 'Create & deploy a starter site',
      steps: [
        {
          id: 'site1',
          kind: 'site.deploy',
          params: { template: params.template ?? 'lyra-starter' },
          preview: 'Deploy to Vercel',
        },
      ],
    };
  }

  // default
  return { summary: 'No known action; chat response only', steps: [] };
}
