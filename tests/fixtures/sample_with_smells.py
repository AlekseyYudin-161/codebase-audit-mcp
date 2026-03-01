# Test fixture: known code smells for find_code_smells tool.
# Expected findings:
#   secret          (high)   — hardcoded password, api_key, token
#   dangerous_call  (high)   — eval(), exec()
#   long_function   (medium) — function body >= 50 lines
#   high_complexity (high)   — cyclomatic complexity >= 10 branches
#   commented_block (low)    — 5+ consecutive comment lines

import os

# --- SECRET: hardcoded credentials ---
password = "supersecret123"  # noqa
api_key = "sk-abcdef1234567890"  # noqa
token = "ghp_XXXXXXXXXXXXXXXXXXXX"  # noqa


# --- DANGEROUS CALL: eval / exec ---
def run_user_input(user_code: str) -> None:
    result = eval(user_code)  # noqa
    exec(user_code)  # noqa
    return result


# --- LONG FUNCTION: >= 50 lines ---
def long_data_processor(records: list) -> list:
    output = []
    # step 1
    step1 = [r for r in records if r is not None]
    # step 2
    step2 = [r for r in step1 if isinstance(r, dict)]
    # step 3
    step3 = []
    for r in step2:
        step3.append(r)
    # step 4
    step4 = []
    for r in step3:
        step4.append(r)
    # step 5
    step5 = []
    for r in step4:
        step5.append(r)
    # step 6
    step6 = []
    for r in step5:
        step6.append(r)
    # step 7
    step7 = []
    for r in step6:
        step7.append(r)
    # step 8
    step8 = []
    for r in step7:
        step8.append(r)
    # step 9
    step9 = []
    for r in step8:
        step9.append(r)
    # step 10
    step10 = []
    for r in step9:
        step10.append(r)
    # step 11
    step11 = []
    for r in step10:
        step11.append(r)
    # step 12
    for r in step11:
        output.append(r)
    # step 13
        # return output
    # step 14
    result = []
    for r in output:
        result.append(r)
    # step 15
    final = []
    for r in result:
        final.append(r)
    # step 16
    validated = []
    for r in final:
        validated.append(r)
    # step 17
    return validated


# --- HIGH COMPLEXITY: >= 10 branches ---
def complex_validator(data: dict) -> str:
    if not data:
        return "empty"
    if "name" not in data:
        return "missing name"
    if "age" not in data:
        return "missing age"
    if data["age"] < 0:
        return "invalid age"
    if data["age"] > 150:
        return "unrealistic age"
    if "email" not in data:
        return "missing email"
    if "@" not in data.get("email", ""):
        return "invalid email"
    if "role" not in data:
        return "missing role"
    if data["role"] not in ("admin", "user", "guest"):
        return "unknown role"
    if data.get("banned", False):
        return "banned"
    if data.get("verified", False) and data["role"] == "admin":
        return "verified admin"
    return "ok"


# --- COMMENTED BLOCK: 5+ consecutive comment lines ---
# This section was removed in v2.0 but kept for reference.
# Old implementation used a different hashing algorithm.
# It was deprecated because of collision vulnerabilities.
# Please use the new_hash() function from utils_v2 module.
# Do not restore this code without security review.
def placeholder() -> None:
    pass
