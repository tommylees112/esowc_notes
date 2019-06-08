def export(
    self,
    variable: str,
    min_year: Optional[int] = 2017,
    max_year: Optional[int] = 2018,
    min_month: Optional[int] = 1,
    max_month: Optional[int] = 12,
    max_leadtime: Optional[int] = None,
    pressure_levels: Optional[int] = None,
    selection_request: Optional[Dict] = None,
    N_parallel_requests: int = 3,
    show_api_request: bool = True,
):
    """
    Arguments
    --------
    min_year: Optional[int] default = 2017
        the minimum year of your request

    max_year: Optional[int] default = 2018
        the maximum year of your request

    min_month: Optional[int] default = 1
        the minimum month of your request

    max_month: Optional[int] default = 12
        the maximum month of your request

    max_leadtime: Optional[int]
        the maximum leadtime of your request
            (if granularity is `hourly` then provide in days)
            (elif granularity is `monthly` then provide in months)
        defaults to ~3 months (90 days)

    pressure_levels: Optional[int]
        Pressure levels to download data at

    Note:
    ----
    - All parameters that are assigned to class attributes are fixed for one download
    - these are required to initialise the object [granularity, pressure_level]
    - Only time will be chunked (by months) to send separate calls to the cdsapi
    """
    # N_parallel_requests can only be a MINIMUM of 1
    if N_parallel_requests < 1:
        N_parallel_requests = 1

    # max_leadtime defaults
    if max_leadtime is None:
        # set the max_leadtime to 3 months as default
        max_leadtime = 90 if (self.granularity == "hourly") else 3

    if pressure_levels is None:
        # set the pressure_levels to ['200', '500', '925'] as default
        pressure_levels = [200, 500, 925] if (self.pressure_level) else None

    processed_selection_request = self.create_selection_request(
        variable=variable,
        max_leadtime=max_leadtime,
        min_year=min_year,
        max_year=max_year,
        min_month=min_month,
        max_month=max_month,
        selection_request=selection_request,
    )

    if self.pressure_level:  # if we are using the pressure_level dataset
        processed_selection_request.update(
            self.get_pressure_levels(pressure_levels)
        )

    if N_parallel_requests > 1:  # Run in parallel
        # p = multiprocessing.Pool(int(N_parallel_requests))
        p = pool(int(N_parallel_requests))  # pathos seems to pickle classes

    # SPLIT THE API CALLS INTO MONTHS (speed up downloads)
    output_paths = []
    updated_requests = []
    for year, month in itertools.product(
        processed_selection_request["year"], processed_selection_request["month"]
    ):
        updated_request = processed_selection_request.copy()
        updated_request["year"] = [year]
        updated_request["month"] = [month]
        updated_requests.append(updated_request)

        if N_parallel_requests > 1:  # Run in parallel
            break

        else:  # run sequentially
            in_parallel = False
            output_paths.append(
                self._export(
                    self.dataset, updated_request,
                    show_api_request, in_parallel
                )
            )

    if N_parallel_requests > 1:
        # multiprocessing of the paths
        in_parallel = True
        output_paths = Parallel(n_jobs=N_parallel_requests)(
            delayed(self._export)(
                dataset=self.dataset,
                selection_request=selection_request,
                show_api_request=show_api_request,
                in_parallel=in_parallel
            ) for selection_request in updated_requests
        )
        # output_paths = p.map(
        #     partial(self._export,
        #             dataset=self.dataset,
        #             show_api_request=show_api_request,
        #             in_parallel=in_parallel)
        #     , updated_requests)

    # close the multiprocessing pool
    if N_parallel_requests > 1:
        p.close()
        p.join()

    return output_paths
