import utils


def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'cf!contests':
        return utils.main()

    if p_message == 'cf!help':
        return "Use cf!contests command to get information "\
            "about coming contests."
