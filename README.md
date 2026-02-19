# Spot-Hopping: High Availability on "Disposable" Infrastructure

> "Don't just use Spot to save money. Use a stateless architecture so your app doesn't even notice when the floor moves beneath it."

Most people fail at Spot Instances because they treat them like cheaper generic servers. They aren't. They are **ephemeral**. To build a robust system, you must handle two things: The **State** and the **Exit**.

## 1. The "Graceful Exit" Pattern (The Missing Dot)

Most tutorials stop at "setting up the fleet". They don't tell you how to handle the **2-minute warning**.

### The Problem
When AWS needs the capacity back, it gives you a 2-minute warning via the Instance Metadata Service. If you ignore this, your application crashes mid-process, leaving corrupted data or "zombie" tasks.

### The Solution: The "Reflex"
We run a **Termination Handler** (`scripts/spot_termination_handler.py`) on every single node.

1.  **Poll**: It checks `http://169.254.169.254/latest/meta-data/spot/instance-action` every 5 seconds.
2.  **Detect**: When it sees a termination notice (HTTP 200), it activates.
3.  **Signal**: It tells the worker process to **STOP** accepting new work immediately.
4.  **Drain**: The worker finishes its *current* task (e.g., 30s) and exits cleanly.

**Result**: The instance disappears, but no work is lost.

## 2. The "State" Pattern

If your worker crashes or vanishes, who remembers what it was doing?

### The Problem
Storing state (e.g., "Scanning IP 10...") in memory or a local file is fatal on Spot.

### The Solution: "Decouple Work from Worker"
We use **Amazon SQS (Simple Queue Service)** as the persistent "Brain".

1.  **Push**: The orchestrator pushes tasks to SQS.
2.  **Pull**: The Spot Instance pulls *one* task.
3.  **Hide**: The task becomes "invisible" to other workers for 60s (Visibility Timeout).
4.  **Delete**: Only *after* the worker successfully finishes, it deletes the message.

**Result**: If a Spot Instance creates a partial failure (dies mid-task), the message "re-appears" in the queue after 60s. Another worker picks it up and finishes it.

## Infrastructure Overview

- **`infra/terraform`**: Sets up the SQS Queue and the Spot Fleet (Auto Scaling Group).
- **`scripts/spot_termination_handler.py`**: The "Reflex" script.
- **`app/worker.py`**: The "Body" script that does the work.

## How to Run

1.  **Deploy Infra**:
    ```bash
    cd infra/terraform
    terraform init && terraform apply
    ```
2.  **The Code**: The `user_data.sh` script automatically installs the handler and worker on boot.

## Cost
See [AWS Cost.md](AWS%20Cost.md) for a breakdown (Spoiler: It's nearly free for testing).
