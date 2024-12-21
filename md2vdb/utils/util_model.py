g_gpt_model = "gpt-4o"
def get_gpt_model():
    global g_gpt_model
    return g_gpt_model

def set_gpt_model(model_name):
    global g_gpt_model
    if model_name in ["gpt-4o", "gpt-4o-mini"]:
        g_gpt_model = model_name
    return g_gpt_model