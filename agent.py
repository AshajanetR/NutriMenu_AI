from agno.agent import Agent, RunResponse  # noqa
from agno.models.groq import Groq

agent = Agent(model=Groq(id="llama-3.3-70b-versatile", api_key="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"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story")