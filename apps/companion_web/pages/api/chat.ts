import type { NextApiRequest, NextApiResponse } from "next";
import { withValidation, withMethodValidation, withContentTypeValidation, CommonSchemas } from "../../lib/validation";
import { ExternalServiceError } from "../../lib/errors";
import { getConfig } from "../../config/environments";

async function chatHandler(
  req: NextApiRequest,
  res: NextApiResponse,
  validated: any
) {
  const { message, mode = "chill" } = validated.body;

  // Check if OpenAI API key is configured
  if (!process.env.OPENAI_API_KEY) {
    return res.status(200).json({ 
      reply: `(demo:${mode}) ${message}`,
      demo: true
    });
  }

  try {
    const apiTimeout = 30000; // 30 seconds timeout
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), apiTimeout);

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: `You are LYRA for AITaskFlo, a ${mode} but helpful assistant. Always be respectful and helpful.`,
          },
          { role: "user", content: message },
        ],
        temperature: 0.7,
        max_tokens: 1000,
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new ExternalServiceError(`OpenAI API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const reply = data?.choices?.[0]?.message?.content;

    if (!reply) {
      throw new ExternalServiceError('No response from OpenAI API');
    }

    return res.status(200).json({ 
      reply,
      usage: data.usage,
      model: data.model
    });
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new ExternalServiceError('Request timeout');
    }
    throw new ExternalServiceError(error?.message || 'Failed to generate response');
  }
}

export default withMethodValidation(['POST'])(
  withContentTypeValidation(['application/json'])(
    withValidation(CommonSchemas.chatMessage)(
      chatHandler
    )
  )
);
