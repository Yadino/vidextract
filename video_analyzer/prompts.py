PROMPT_TEMPLATE = (
    "I have this analysis of a video in JSON format which includes:\n\n"
    "A description of detected objected in each shot.\n\n"
    "A description of a still from each shot (in caption, unless caption is null).\n\n"
    "A description of sound events extracted from each second of the video.\n\n"
    "A transcript of the English speech spoken in the video.\n\n"
    "You need to:\n"
    "Select important moments in the video (e.g., explosions, people speaking, vehicle movement).\n"
    "Generate detailed descriptions for each moment.\n"
    "Return the results in a JSON format like so:\n\n"
    '{{\n'
    '    "moments": [\n'
    '        {{\n'
    '            "shot_numbers": [],\n'
    '            "start_time": 0.0,\n'
    '            "end_time": 0.0,\n'
    '            "description": ""\n'
    '        }}\n'
    '    ]\n'
    '}}\n\n'
    "You may approximate the start and end time to the best of your judgement.\n"
    "You may also use your best judgement to decide which moments are important, the video's title may or may not be helpful to decide that.\n"
    "Use ONLY JSON format for the output.\n"
    "DO NOT deliver partial output or digress in any way from the provided JSON format.\n\n"
    "Example output:\n\n"
    '{{\n'
    '  "moments": [\n'
    '    {{\n'
    '      "shot_numbers": [0],\n'
    '      "start_time": 0,\n'
    '      "end_time": 8,\n'
    '      "description": "A wedding photoshoot is in progress with people speaking in the background. The setting includes benches and potted plants, likely in an outdoor or public location."\n'
    '    }},\n'
    '    {{\n'
    '      "shot_numbers": [1],\n'
    '      "start_time": 14.5,\n'
    '      "end_time": 15.5,\n'
    '      "description": "A large explosion occurs, disrupting the scene. People are running and shouting."\n'
    '    }}\n'
    '  ]\n'
    '}}\n\n'
    "END OF EXAMPLE.\n\n"
    "Below is the video analysis to extract important moments from:\n\n"
    "{json_schema}"
) 