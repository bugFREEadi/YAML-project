# Declarative Multi-Agent Orchestration Using YAML - Hackathon Evaluation (Hindi Version)

## 1. Problem Statement Explanation

### Problem kya solve ho rahi hai?
Ye project multi-agent AI systems banane ki complexity ko solve karta hai. Usually, agar humein ek aisa system banana ho jisme multiple AI agents milke kaam karein, toh humein bahut complex Python code likhna padta hai. State maintain karna, API calls handle karna, aur agents ko connect karna mushkil ho jata hai.

### Current approaches kyu mushkil hain?
- **Bahut Sara Code**: Har choti cheez ke liye code likhna padta hai.
- **Visualise karna mushkil hai**: Sirf code dekh kar samajh nahi aata ki agents kaise interact kar rahe hain.
- **Vendor Lock-in**: Kayi frameworks ek hi provider (jaise OpenAI) se bandhe hote hain.
- **Debugging Mushkil hai**: Jab agents aapas mein baat karte hain aur kuch galti hoti hai, toh pata lagana mushkil hota hai ki kahan galti hui.

### YAML-based orchestration kaise help karta hai?
- **Declarative Approach**: Aap bas YAML file mein likhte hain ki aapko *kya* chahiye (konsa agent, kya role), aur system khud decide karta hai ki wo *kaise* hoga.
- **Language Agnostic**: Logic simple text (YAML) mein hai, toh ise samajhna aur share karna aasaan hai.
- **Fast Prototyping**: Agar agent change karna hai ya flow badalna hai, toh bas YAML mein 2 line change karo, code likhne ki zaroorat nahi.

---

## 2. My Approach (Mera Tareeka)

### Overall Architecture
Mera system ek **Modular Orchestration Engine** hai.
1.  **Input**: Ek simple YAML file.
2.  **Validator**: Ye check karta hai ki YAML sahi hai ya nahi.
3.  **Executor**: Ye main engine hai jo workflow ko chalata hai.
4.  **Agent Runtimes**: Har agent ke liye alag environment (OpenAI, Gemini, etc.).
5.  **Output Formatter**: Final result ko sundar aur structured tareeke se dikhata hai.

### YAML ka use kaise hota hai?
- **Agents**: Hum YAML mein agents define karte hain - unka `id`, `role`, `goal`, aur `model`. Hum `sub_agents` bhi bana sakte hain.
- **Workflow**: `workflow` section mein hum batate hain ki kaam `sequential` (ek ke baad ek) hoga ya `parallel` (saath mein).

### Step-by-Step Execution
1.  **Load & Validate**: System YAML padhta hai aur errors check karta hai.
2.  **Graph Construction**: Memory mein workflow ka map banata hai.
3.  **Execution Loop**:
    -   **Sequential**: Agents ek ke baad ek chalte hain.
    -   **Parallel**: Threads use karke agents saath mein chalte hain aur result combine hota hai.
    -   **Context Passing**: Pichle agent ka output agle agent ko context ki tarah milta hai.
4.  **Final Output**: Last mein sab kuch compile karke dikhaya jata hai.

---

## 3. Files Explanation

### `run.py` (Command Center)
- **Kaam**: Ye project ka entry point hai.
- **Kyu**: Ye user se file ka naam leta hai, validator ko call karta hai, aur phir execution start karta hai. Errors ko bhi yehi sambhalta hai.

### `backend/validator.py` (Security Guard)
- **Kaam**: YAML file ko check karna.
- **Kyu**: Ye ensure karta hai ki koi agent missing na ho, ya koi infinite loop na ban jaye. Ye run hone se pehle hi galti pakad leta hai.

### `backend/executor.py` (Main Engine)
- **Kaam**: Asli kaam yahin hota hai.
- **Details**: Isme `run_agent` function hai jo agent ko chalata hai, tools manage karta hai, aur `process_step` function hai jo workflow ko aage badhata hai.

### `backend/agent.py` (Template)
- **Kaam**: Har agent ka structure define karta hai.
- **Details**: Ye agent ka prompt banata hai jisme uska role, goal, aur context mix hota hai.

### `backend/models/router.py` (Model Manager)
- **Kaam**: Alag-alag AI models (OpenAI, Gemini, Claude) se baat karna.
- **Kyu**: Agar humein model change karna ho, toh code change nahi karna padta, bas YAML mein naam badal do.

### `backend/output_formatter.py` (Presenter)
- **Kaam**: User ko result dikhana.
- **Kyu**: Ye 4 sections mein output deta hai taaki user aasani se samajh sake ki kya hua.

---

## 4. Implementation Details

### How YAML is parsed
Main Python ki `PyYAML` library use karta hu configuration load karne ke liye.

### API Calls
`router.py` file mein har provider (OpenAI, Google) ke liye alag function hai. Maine error handling lagayi hai, taaki agar API key galat ho ya internet na ho, toh system crash na kare, balki proper error message de.

### Sequential vs. Parallel
- **Sequential**: Simple loop chalta hai. Ek ka output agle ke input mein judta jata hai.
- **Parallel**: Python ki `ThreadPoolExecutor` use ki hai. Agents alag-alag threads mein chalte hain, aur phir `then` block mein unka result combine hota hai.

### Output Generation
Sabse zaroori cheez - mera code ek global `EXECUTION_LOG` maintain karta hai. Chahe sub-agents ho ya tools, sab kuch is log mein save hota hai. `output_formatter.py` isi log ko padh kar final report banata hai, isliye koi data miss nahi hota.

---

## 5. Results & Demo Flow

### Input
Mai ek simple file `calculator.yaml` deta hu. Isme ek "Math Expert" hai aur ek "Python Analyst".

### Output
System terminal pe 4 sections print karta hai:
1.  **Diagram**: Flow chart dikhata hai (kaun kiske baad chala).
2.  **Responses**: Har agent ne kya bola.
3.  **Reviewer Summary**: Agar koi reviewer hai toh uska review.
4.  **Trace Table**: Table jisme likha hota hai kisne konsa model use kiya.

### Why is this useful?
Isse complex AI system banana "config file likhne" jitna aasaan ho jata hai. Koi bhi bina Python code likhe AI agents ki team bana sakta hai.

---

## 6. Judges Pitch (30-40 Seconds) - Hinglish

"Namaste, maine ek **Declarative Multi-Agent Orchestration Engine** banaya hai.

**Problem**: Aaj multi-agent systems banana bahut complex hai. Do agents ko connect karne ke liye bhi humein heavy aur error-prone code likhna padta hai.

**Solution**: Maine saari complexity ko ek **YAML-based engine** mein move kar diya hai. Aap bas English aur YAML mein apne agents 'program' karte hain. Aap batate hain ki wo kaun hai, unke paas kya tools hain (jaise calculator), aur wo kaise connect honge—sequentially ya parallel.

**Under the hood**: Mera engine parallel threading, context aggregation, model routing (OpenAI/Gemini), aur error safety khud handle karta hai.

**Result**: Aap bina Python code likhe, sirf 30 seconds mein ek complex AI team bana sakte hain. Ye clean hai, visual hai, aur stable hai."
