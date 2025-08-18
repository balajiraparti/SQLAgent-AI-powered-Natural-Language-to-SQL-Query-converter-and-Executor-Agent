import replicate

input = {
    "top_p": 0.9,
    "prompt": "Story title: 3 llamas go for a walk\nSummary: The 3 llamas crossed a bridge and something unexpected happened\n\nOnce upon a time",
    "min_tokens": 0,
    "temperature": 0.6,
    "presence_penalty": 1.15
}

for event in replicate.stream(
    "meta/meta-llama-3-8b",
    input=input
):
    print(event, end="")
#=> " there were 3 llamas. They were very friendly and they d...