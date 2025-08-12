import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { update } from '../_store';

export async function POST(req: NextRequest) {
  const { owner_email, public_name, model } = await req.json();
  const id = crypto.randomBytes(8).toString('hex');
  const secret = crypto.randomBytes(16).toString('hex');
  update(id, { owner_email, public_name, model });
  return NextResponse.json({ ok: true, id, secret });
}

