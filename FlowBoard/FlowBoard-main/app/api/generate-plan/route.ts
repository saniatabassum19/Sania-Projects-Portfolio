import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const body = await req.json();

    const prompt = `
You are a senior full-stack architect.

A user has created a VERY BASIC application flow with limited nodes.
The flow is incomplete and represents only high-level intent.

Your job is to EXPAND this into a complete, production-ready system design.

---

FLOW INPUT:
${JSON.stringify(body, null, 2)}

---

IMPORTANT:
- The user flow is incomplete
- You must infer missing steps, validations, and flows
- Think like a real product engineer

---

Generate a clean response in plain text (NO markdown symbols like #, *, -)

---

Follow this structure:

SYSTEM UNDERSTANDING
Explain what the user is trying to build.

EXPANDED USER FLOW
Describe the FULL flow including missing steps (cart, validation, retries, etc).

FEATURES
List all features inferred from the system.

FRONTEND STRUCTURE
List screens/pages and what each does.

BACKEND DESIGN
List APIs with method and purpose.

DATA FLOW
Explain how data moves through the system step-by-step.

EDGE CASES
List failure scenarios (payment fail, stock unavailable, invalid input, etc).

PROJECT STRUCTURE
Show folder structure for frontend (Next.js) and backend (FastAPI).

STARTER CODE
Provide minimal working examples:
- One frontend page
- One backend route

BUILD PROMPT
Generate a high-quality prompt that can be copy-pasted into AI tools like Lovable to generate the full app.

---

RULES:
- Be practical and realistic
- Fill missing gaps intelligently
- Keep it structured and readable
- No markdown formatting
`;

    const response = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" +
        process.env.GEMINI_API_KEY,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                contents: [
                    {
                        parts: [{ text: prompt }],
                    },
                ],
            }),
        }
    );

    const data = await response.json();
    console.log("FULL GEMINI RESPONSE:", JSON.stringify(data, null, 2));
    console.log("API KEY RAW:", process.env.GEMINI_API_KEY);

    const result =
        data.candidates?.[0]?.content?.parts?.[0]?.text || "No response";

    return NextResponse.json({ result });
}