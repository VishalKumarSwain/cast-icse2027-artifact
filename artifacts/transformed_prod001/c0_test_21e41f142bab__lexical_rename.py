from transformers import AutoModelForQuestionAnswering, AutoTokenizer

class QuestionAnsweringModel:

    def __init__(self, model_checkpoint, max_length, doc_stride, impossible_answer):
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        self.max_length = max_length
        self.doc_stride = doc_stride
        self.impossible_answer = impossible_answer


    def prepare_model(self):
        return self.model, self.tokenizer

    def predict(self, question, context):
        # Tokenize question and context
        inputs_renamed = self.tokenizer(question, context, max_length=self.max_length, stride=self.doc_stride, return_tensors="pt")

        # Generate answer start and end logits
        outputs = self.model(**inputs_renamed)
        start_logits = outputs.start_logits
        end_logits = outputs.end_logits

        # Find the most likely start and end positions
        start_index = start_logits.argmax()
        end_index = end_logits.argmax()

        # Return answer
        return self.tokenizer.decode(inputs_renamed["input_ids"][0][start_index:end_index + 1])
