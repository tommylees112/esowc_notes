from scripts.utils import get_data_path
from src.analysis import all_shap_for_file
from src.models import (
    Persistence,
    LinearRegression,
    LinearNetwork,
    RecurrentNetwork,
    EARecurrentNetwork,
    load_model,
    GBDT,
)
import sys

sys.path.append("..")

# def


def parsimonious(experiment="one_month_forecast",):
    predictor = Persistence(get_data_path(), experiment=experiment)
    predictor.evaluate(save_preds=True)


def regression(
    experiment="one_month_forecast",
    include_pred_month=True,
    surrounding_pixels=1,
    explain=False,
):
    predictor = LinearRegression(
        get_data_path(),
        experiment=experiment,
        include_pred_month=include_pred_month,
        surrounding_pixels=surrounding_pixels,
        static="embeddings",
    )
    predictor.train()
    predictor.evaluate(save_preds=True)

    # mostly to test it works
    if explain:
        predictor.explain(save_shap_values=True)


def linear_nn(
    experiment="one_month_forecast",
    include_pred_month=True,
    surrounding_pixels=1,
    explain=False,
):
    predictor = LinearNetwork(
        layer_sizes=[100],
        data_folder=get_data_path(),
        experiment=experiment,
        include_pred_month=include_pred_month,
        surrounding_pixels=surrounding_pixels,
    )
    predictor.train(num_epochs=50, early_stopping=5)
    predictor.evaluate(save_preds=True)
    predictor.save_model()

    if explain:
        _ = predictor.explain(save_shap_values=True)


def rnn(
    experiment="one_month_forecast",
    include_pred_month=True,
    surrounding_pixels=1,
    explain=False,
):
    predictor = RecurrentNetwork(
        hidden_size=128,
        data_folder=get_data_path(),
        experiment=experiment,
        include_pred_month=include_pred_month,
        surrounding_pixels=surrounding_pixels,
    )
    predictor.train(num_epochs=50, early_stopping=5)
    predictor.evaluate(save_preds=True)
    predictor.save_model()

    if explain:
        _ = predictor.explain(save_shap_values=True)


def earnn(
    experiment="one_month_forecast",
    include_pred_month=True,
    surrounding_pixels=None,
    pretrained=True,
    explain=False,
):
    data_path = get_data_path()

    if not pretrained:
        predictor = EARecurrentNetwork(
            hidden_size=128,
            data_folder=data_path,
            experiment=experiment,
            include_pred_month=include_pred_month,
            surrounding_pixels=surrounding_pixels,
        )
        predictor.train(num_epochs=50, early_stopping=5)
        predictor.evaluate(save_preds=True)
        predictor.save_model()
    else:
        predictor = load_model(data_path / f"models/{experiment}/ealstm/model.pt")

    if explain:
        test_file = data_path / f"features/{experiment}/test/2018_3"
        assert test_file.exists()
        all_shap_for_file(test_file, predictor, batch_size=100)


def gbdt(
    experiment="one_month_forecast",
    include_pred_month=True,
    surrounding_pixels=None,
    pretrained=True,
    explain=False,
):
    data_path = get_data_path()

    # initialise, train and save GBDT model
    predictor = GBDT(
        data_folder=data_path,
        experiment=experiment,
        include_pred_month=include_pred_month,
        surrounding_pixels=surrounding_pixels,
        static="embedding",
    )
    predictor.train(early_stopping=5)
    predictor.evaluate(save_preds=True)
    predictor.save_model()


if __name__ == "__main__":
    #

    # fit the models for this
    parsimonious()
    regression()
    linear_nn()
    rnn()
    earnn()
    # gbdt()
