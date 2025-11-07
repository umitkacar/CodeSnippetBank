"""
LLM Fine-tuning
Prepare datasets and fine-tune LLMs with OpenAI and HuggingFace.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import time

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class TrainingExample:
    """Container for training example."""
    messages: List[Dict[str, str]]
    system_message: Optional[str] = None


class DatasetPreparation:
    """Prepare datasets for fine-tuning."""

    @staticmethod
    def create_chat_format(
        examples: List[TrainingExample]
    ) -> List[Dict[str, Any]]:
        """
        Convert examples to chat format.

        Args:
            examples: List of training examples

        Returns:
            List of formatted examples
        """
        formatted = []

        for example in examples:
            messages = []

            if example.system_message:
                messages.append({
                    "role": "system",
                    "content": example.system_message
                })

            messages.extend(example.messages)

            formatted.append({"messages": messages})

        return formatted

    @staticmethod
    def create_completion_format(
        prompts: List[str],
        completions: List[str]
    ) -> List[Dict[str, str]]:
        """
        Create completion format for fine-tuning.

        Args:
            prompts: List of prompts
            completions: List of completions

        Returns:
            List of formatted examples
        """
        return [
            {"prompt": prompt, "completion": completion}
            for prompt, completion in zip(prompts, completions)
        ]

    @staticmethod
    def save_jsonl(
        data: List[Dict[str, Any]],
        filepath: str
    ):
        """
        Save data in JSONL format.

        Args:
            data: List of examples
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')

    @staticmethod
    def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
        """
        Load data from JSONL format.

        Args:
            filepath: Input file path

        Returns:
            List of examples
        """
        data = []

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))

        return data

    @staticmethod
    def validate_format(
        data: List[Dict[str, Any]],
        format_type: str = "chat"
    ) -> Tuple[bool, List[str]]:
        """
        Validate dataset format.

        Args:
            data: Dataset to validate
            format_type: "chat" or "completion"

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        for i, item in enumerate(data):
            if format_type == "chat":
                if "messages" not in item:
                    errors.append(f"Item {i}: Missing 'messages' field")
                    continue

                for j, msg in enumerate(item["messages"]):
                    if "role" not in msg:
                        errors.append(f"Item {i}, message {j}: Missing 'role'")
                    if "content" not in msg:
                        errors.append(f"Item {i}, message {j}: Missing 'content'")

            elif format_type == "completion":
                if "prompt" not in item:
                    errors.append(f"Item {i}: Missing 'prompt'")
                if "completion" not in item:
                    errors.append(f"Item {i}: Missing 'completion'")

        return len(errors) == 0, errors


class OpenAIFineTuning:
    """Fine-tune models with OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI fine-tuning.

        Args:
            api_key: OpenAI API key
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def upload_training_file(self, filepath: str) -> str:
        """
        Upload training file to OpenAI.

        Args:
            filepath: Path to JSONL file

        Returns:
            File ID
        """
        with open(filepath, 'rb') as f:
            response = self.client.files.create(
                file=f,
                purpose='fine-tune'
            )

        return response.id

    def create_fine_tune_job(
        self,
        file_id: str,
        model: str = "gpt-3.5-turbo",
        suffix: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create fine-tuning job.

        Args:
            file_id: Training file ID
            model: Base model to fine-tune
            suffix: Optional suffix for fine-tuned model name
            hyperparameters: Training hyperparameters

        Returns:
            Fine-tune job ID
        """
        kwargs = {
            "training_file": file_id,
            "model": model
        }

        if suffix:
            kwargs["suffix"] = suffix

        if hyperparameters:
            kwargs["hyperparameters"] = hyperparameters

        response = self.client.fine_tuning.jobs.create(**kwargs)

        return response.id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get fine-tuning job status.

        Args:
            job_id: Job ID

        Returns:
            Job status dictionary
        """
        job = self.client.fine_tuning.jobs.retrieve(job_id)

        return {
            "id": job.id,
            "status": job.status,
            "model": job.fine_tuned_model,
            "created_at": job.created_at,
            "finished_at": job.finished_at,
            "error": job.error
        }

    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 60
    ) -> str:
        """
        Wait for fine-tuning job to complete.

        Args:
            job_id: Job ID
            poll_interval: Polling interval in seconds

        Returns:
            Fine-tuned model name
        """
        print(f"Waiting for fine-tuning job {job_id}...")

        while True:
            status = self.get_job_status(job_id)

            print(f"Status: {status['status']}")

            if status['status'] == 'succeeded':
                print(f"Fine-tuning complete! Model: {status['model']}")
                return status['model']

            elif status['status'] in ['failed', 'cancelled']:
                raise Exception(f"Fine-tuning failed: {status['error']}")

            time.sleep(poll_interval)

    def list_fine_tuned_models(self) -> List[Dict[str, Any]]:
        """
        List all fine-tuned models.

        Returns:
            List of model information
        """
        jobs = self.client.fine_tuning.jobs.list()

        return [
            {
                "id": job.id,
                "model": job.fine_tuned_model,
                "status": job.status,
                "created_at": job.created_at
            }
            for job in jobs.data
            if job.fine_tuned_model
        ]


class HuggingFaceFineTuning:
    """Fine-tune models with HuggingFace Transformers."""

    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize HuggingFace fine-tuning.

        Args:
            model_name: Base model name
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed")

        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def prepare_dataset(
        self,
        texts: List[str],
        max_length: int = 512
    ) -> Dataset:
        """
        Prepare dataset for training.

        Args:
            texts: List of training texts
            max_length: Maximum sequence length

        Returns:
            Dataset object
        """
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                max_length=max_length,
                padding='max_length'
            )

        # Create dataset
        dataset = Dataset.from_dict({"text": texts})

        # Tokenize
        tokenized = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )

        return tokenized

    def train(
        self,
        train_dataset: Dataset,
        output_dir: str,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
        warmup_steps: int = 500,
        save_steps: int = 1000
    ):
        """
        Train the model.

        Args:
            train_dataset: Training dataset
            output_dir: Output directory for checkpoints
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            warmup_steps: Warmup steps
            save_steps: Save checkpoint every N steps
        """
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            save_steps=save_steps,
            save_total_limit=3,
            logging_steps=100,
            evaluation_strategy="no",
            fp16=torch.cuda.is_available()
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator
        )

        trainer.train()

        # Save final model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

    def generate(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.8
    ) -> str:
        """
        Generate text with fine-tuned model.

        Args:
            prompt: Input prompt
            max_length: Maximum generation length
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        inputs = self.tokenizer(prompt, return_tensors="pt")

        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


# Usage Examples
if __name__ == "__main__":
    # Example 1: Prepare dataset
    print("=== Dataset Preparation ===")

    examples = [
        TrainingExample(
            system_message="You are a Python expert.",
            messages=[
                {"role": "user", "content": "How do I reverse a string?"},
                {"role": "assistant", "content": "Use slicing: string[::-1]"}
            ]
        ),
        TrainingExample(
            system_message="You are a Python expert.",
            messages=[
                {"role": "user", "content": "How do I sort a list?"},
                {"role": "assistant", "content": "Use list.sort() or sorted(list)"}
            ]
        )
    ]

    prep = DatasetPreparation()
    chat_data = prep.create_chat_format(examples)

    print(f"Created {len(chat_data)} training examples")
    print(f"Example: {chat_data[0]}\n")

    # Save to file
    prep.save_jsonl(chat_data, "/tmp/training_data.jsonl")
    print("Saved to /tmp/training_data.jsonl\n")

    # Validate
    loaded = prep.load_jsonl("/tmp/training_data.jsonl")
    is_valid, errors = prep.validate_format(loaded, "chat")
    print(f"Dataset valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}\n")

    # Example 2: OpenAI Fine-tuning (requires API key)
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        print("=== OpenAI Fine-Tuning ===")
        ft = OpenAIFineTuning()

        # Upload file
        # file_id = ft.upload_training_file("/tmp/training_data.jsonl")
        # print(f"Uploaded file: {file_id}")

        # Create job
        # job_id = ft.create_fine_tune_job(file_id, model="gpt-3.5-turbo")
        # print(f"Created job: {job_id}")

        # List models
        models = ft.list_fine_tuned_models()
        print(f"Fine-tuned models: {len(models)}\n")

    # Example 3: HuggingFace Fine-tuning
    if TRANSFORMERS_AVAILABLE:
        print("=== HuggingFace Fine-Tuning ===")

        training_texts = [
            "Python is a great programming language.",
            "Machine learning is fascinating.",
            "Deep learning uses neural networks."
        ]

        hf_ft = HuggingFaceFineTuning("gpt2")
        dataset = hf_ft.prepare_dataset(training_texts)

        print(f"Prepared dataset with {len(dataset)} examples")
        # hf_ft.train(dataset, output_dir="/tmp/fine_tuned_model")
