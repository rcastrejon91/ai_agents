import { test, expect, request } from "@playwright/test";

const BASE = process.env.BASE_URL!;
const ADMIN = process.env.ADMIN_TOKEN!;

test.describe("Graph-grounded answering", () => {
  test("abstains with no evidence, answers with seeded evidence", async ({}) => {
    const api = await request.newContext({ baseURL: BASE });

    let r = await api.get("/api/med/graph/test_clear", {
      headers: { Authorization: `Bearer ${ADMIN}` },
    });
    expect(r.ok()).toBeTruthy();

    r = await api.post("/api/med/graph/query", {
      data: { question: "Does albuterol treat asthma?" },
    });
    let j = await r.json();
    expect(r.ok()).toBeTruthy();
    expect(j.abstain).toBeTruthy();

    r = await api.get("/api/med/graph/test_seed", {
      headers: { Authorization: `Bearer ${ADMIN}` },
    });
    expect(r.ok()).toBeTruthy();

    r = await api.post("/api/med/graph/query", {
      data: { question: "Does albuterol treat asthma?" },
    });
    j = await r.json();
    expect(r.ok()).toBeTruthy();
    expect(j.abstain).toBeFalsy();
    expect(j.edges).toBeGreaterThan(0);
    expect(String(j.answer)).toMatch(/albuterol/i);
  });
});
