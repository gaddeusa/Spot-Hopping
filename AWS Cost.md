# AWS Infrastructure Cost Analysis

This document outlines the estimated costs for running the "Spot-Hopping" architecture on AWS.

## 1. Compute: Spot Instances (The "Workers")

We use small, burstable instances for testing and lightweight workloads.

*   **Instance Type**: `t3.micro` (2 vCPU, 1 GB RAM) or `t3a.micro`.
*   **Market**: Spot Instances (Spare EC2 capacity).
*   **Hourly Cost**: ~$0.003 - $0.004 per hour (varies by region/availability zone).
*   **Monthly Cost (per instance, 24/7)**: ~$2.50 USD.
    *   *Calculation*: $0.0035 * 24 hours * 30 days = $2.52.

**Note**: Spot prices fluctuate but are typically 70-90% cheaper than On-Demand prices (~$0.0104/hr for t3.micro).

## 2. Queue: Simple Queue Service (The "Brain")

SQS is used to manage state and buffer tasks between worker interruptions.

*   **Tier**: AWS Free Tier.
*   **Free Allowance**: First **1 Million Requests** per month are free.
*   **Overage Cost**: $0.40 per 1 million requests thereafter.
*   **Estimated Cost**: **$0.00** (It is highly unlikely to exceed 1M requests during testing or small-scale usage).

## 3. Data Transfer & Networking

*   **Instance Metadata (Polling)**:
    *   **Cost**: **$0.00**.
    *   **Reason**: Traffic to `169.254.169.254` is link-local and stays within the physical host. It is not billed.
*   **SQS Traffic**:
    *   **Cost**: **$0.00**.
    *   **Reason**: Data transfer between EC2 and SQS in the same region is free.
*   **Outbound Internet Traffic**:
    *   AWS standard rates apply (First 100GB/month is free).
    *   *Relevance*: Only if your worker script downloads large files from the external internet.

## Total Estimated Monthly Cost

| Resource | Usage (Est.) | Monthly Cost |
| :--- | :--- | :--- |
| **Spot Instance (t3.micro)** | 1 instance, 24/7 | ~$2.52 |
| **SQS Standard Queue** | < 1M requests | $0.00 |
| **Data Transfer** | Minimal | $0.00 |
| **Total** | | **~$2.52 USD** |

*Disclaimer: Prices are estimates based on us-east-1 region and current Spot market rates. Always set up AWS Budgets to monitor actual usage.*
