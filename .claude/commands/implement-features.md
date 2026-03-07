# Instruction

Use the `get_oldest_approved_request` tool to get the next feature to implement. If there is one, mark it as "in progress", then launch the mcp-feature-developer agent.

Launch the `mcp-feature-developer` agent, giving it the information contained in the request. Do not give implementation instructions outside of those contained in the request.
If the feature successfully implements the feature, mark the request as "implemented" and fetch the next request. Do this sequentially, and repeat until all of the requested features have been implemented or are otherwise blocked.
