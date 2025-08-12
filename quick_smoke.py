import asyncio

from frontend_agent import FrontendAgent


async def main() -> None:
    agent = FrontendAgent()
    out = await agent.handle({"text": "I'm angry at this bug but hopeful"})
    print(out)


if __name__ == "__main__":
    asyncio.run(main())

