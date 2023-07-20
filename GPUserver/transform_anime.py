from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import ImageInput
from custom_artifact import CustomModelArtifact

@env(infer_pip_packages=True)
@artifacts([CustomModelArtifact('model')])
class Transform_Anime(BentoService):

    @api(input=ImageInput(), mb_max_latency=10000, mb_max_batch_size=100000, batch=True)
    def transform(self, image, input_bbox, prompt):
        return self.artifacts.model.pipe(image, input_bbox, prompt)