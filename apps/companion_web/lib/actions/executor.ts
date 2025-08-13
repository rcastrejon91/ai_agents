import { requestRideDeepLink } from './integrations/rides';
import { transferFunds } from './integrations/payments';
import { searchTravel, bookTravel } from './integrations/travel';
import { searchLodging, requestLodging } from './integrations/lodging';
import { postSocial } from './integrations/social';
import { deploySite } from './integrations/deploy';
import { callStore } from './integrations/voice';

export async function executePlan(plan: any) {
  const results: any[] = [];
  for (const step of plan.steps) {
    if (step.kind === 'rides.request') results.push(await requestRideDeepLink(step.params));
    else if (step.kind === 'payments.transfer') results.push(await transferFunds(step.params));
    else if (step.kind === 'travel.search') results.push(await searchTravel(step.params));
    else if (step.kind === 'travel.book') results.push(await bookTravel(step.params));
    else if (step.kind === 'lodging.search') results.push(await searchLodging(step.params));
    else if (step.kind === 'lodging.request') results.push(await requestLodging(step.params));
    else if (step.kind === 'social.post') results.push(await postSocial(step.params));
    else if (step.kind === 'site.deploy') results.push(await deploySite(step.params));
    else if (step.kind === 'voice.call') results.push(await callStore(step.params));
    else results.push({ step: step.id, skipped: true });
  }
  return { plan: plan.summary, steps: plan.steps.length, results };
}
