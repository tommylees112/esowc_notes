def test_ouce_get_fnames(self, tmp_dir):
    o = OuceS5Data()
    out_dir = Path("/lustre/soge1/data/incoming/seas5/1.0x1.0/6-hourly")
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
    fnames = [
        out_dir / f"seas5_6-hourly_2m_temperature_20070{i}.nc" for i in range(1, 6)
    ]

    [f.touch() for f in fnames]
    rmtree(out_dir)
