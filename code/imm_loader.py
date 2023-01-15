from dataclasses import dataclass, field

import nltk


@dataclass(kw_only=True, slots=True,)
class DocumentSample:
    file_name: str
    n_opinions: int
    minimum: int
    maximum: int
    average: float
    standard_deviation: float
    simplified: int
    annotator_labels: list[int]
    sign_conflict: bool
    document_id: str = field(init=False)

    def __post_init__(self):
        self.document_id = self.file_name.split('flashback-')[-1]


@dataclass(kw_only=True, slots=True,)
class ParagraphSample(DocumentSample):
    paragraph_id: int
    title: bool
    text: str
    tokenized_text: list[str] = field(init=False)


    def __post_init__(self):
        super(ParagraphSample, self).__post_init__()
        self.tokenized_text = [token.lower() for token in nltk.word_tokenize(self.text)]

    def __hash__(self) -> int:
        return hash((self.document_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ParagraphSample):
            return self.document_id == __o.document_id
        return False


class DocumentLoader:
    def __init__(self, path, source='flashback') -> None:
        self.samples: list[DocumentSample] = []

        with open(path, 'r', encoding='utf-8') as annotations:
            lines = annotations.readlines()
        for line in lines[1:]:
            (file_name,
             n_opinions,
             minimum,
             maximum,
             average,
             standard_deviation,
             simplified,
             *annotator_labels,
             sign_conflict) = line.rstrip('\n').split('\t')

            if source in file_name:
                self.samples.append(DocumentSample(
                    file_name=file_name,
                    n_opinions=int(n_opinions),
                    minimum=int(minimum),
                    maximum=int(maximum),
                    average=float(average),
                    standard_deviation=float(standard_deviation),
                    simplified=int(simplified),
                    annotator_labels=[int(label)
                                      if label != '' else -1
                                      for label in annotator_labels],
                    sign_conflict=bool(sign_conflict)
                ))


class ParagraphLoader:
    def __init__(self, path, source='flashback') -> None:
        self.samples: list[ParagraphSample] = []

        with open(path, 'r', encoding='utf-8') as annotations:
            lines = annotations.readlines()
        for line in lines[1:]:
            (file_name,
             paragraph_id,
             n_opinions,
             minimum,
             maximum,
             average,
             standard_deviation,
             simplified,
             *annotator_labels,
             sign_conflict,
             title,
             text) = line.rstrip('\n').split('\t')

            if source in file_name:
                self.samples.append(ParagraphSample(
                    file_name=file_name,
                    paragraph_id=int(paragraph_id),
                    n_opinions=int(n_opinions),
                    minimum=int(minimum),
                    maximum=int(maximum),
                    average=float(average),
                    standard_deviation=float(standard_deviation),
                    simplified=int(simplified),
                    annotator_labels=[int(label)
                                      if label != '' else -1
                                      for label in annotator_labels],
                    sign_conflict=bool(sign_conflict),
                    title=bool(title),
                    text=text
                ))
