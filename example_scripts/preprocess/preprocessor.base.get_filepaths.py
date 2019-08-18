def get_filepaths(self, folder: str = 'raw',
                  years: Optional[List[int]] = None) -> List[Path]:
    if folder == 'raw':
        target_folder = self.raw_folder / self.dataset
    else:
        target_folder = self.interim

    if years is not None:
        assert int(list(target_folder.glob('**'))[0])  # type: ignore
        outfiles = [
            f for f in target_folder.glob('**/*.nc')
            if int(f.parents[0]) in years  # type: ignore
        ]
    else:
        outfiles = [
            f for f in target_folder.glob('**/*.nc')
        ]

    outfiles.sort()
    return outfiles
