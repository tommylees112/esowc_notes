#  try_get_non_target_vars.py


@staticmethod
def move_target_var_to_end_of_dataset(x: xr.Dataset, y: xr.Dataset) -> xr.Dataset:
    # @GABI is this a sensible way to ensure we always have the `target` last?
    # get the x_vars and target_var
    target_var = [y for y in y.data_vars][0]
    all_vars = [v for v in x.data_vars]
    x_vars = [x_var for x_var in x.data_vars if x_var != target_var]

    # reorganise so that target is always last
    new_x = x[x_vars]
    x = xr.merge([new_x, x[target_var]])
    new_x_vars = [x_var for x_var in x.data_vars]
    target_var_index = int(np.argwhere(np.isin(new_x_vars, [target_var])))
    assert target_var_index == len(all_vars) - 1, (
        f"Expect the target variable" " to be the final variable in the `x` dataset"
    )

    return x


if self.experiment == "nowcast":
    vars = [v for v in x.data_vars]
    assert len(vars) > 1, "Must have more than target variable for nowcast"
    # move the target variable to the final variable index
    x = self.move_target_var_to_end_of_dataset(x=x, y=y)


current = x_np[:, -1, :-1]  # only select the NON-TARGET variables
