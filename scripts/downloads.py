import os
import glob


FIPS = ('01', '02', '04', '05', '06', '08', '09', '10', '11', '12', '13', '15',
        '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27',
        '28', '29', '30', '31' ,'32', '33', '34', '35', '36', '37', '38', '39',
        '40', '41', '42', '44', '45', '46', '47', '48', '49', '50', '51', '53',
        '54', '55', '56', '60', '66', '69', '72', '78')


def download_file(url, where):
    # create directory and work in it
    pop = os.path.abspath(os.getcwd())
    if not os.path.exists(where):
        os.makedirs(where)
    os.chdir(where)

    fname = os.path.basename(url)
    if not os.path.exists(fname):
        os.system('wget %s' % (url))

    os.chdir(pop)


def download_census_file(top, fips, what, year, where):

    if year == "13":
        url = ("ftp://ftp2.census.gov/geo/tiger/{top}"
               "/{fips}/tl_rd{year}_{fips}_{what}.zip").format(**{
                   "year": year,
                   "what": what,
                   "fips": fips,
                   "top": top,
               })
    else:
        url = ("ftp://ftp2.census.gov/geo/tiger/{top}"
               "/{WHAT}/tl_{year}_{fips}_{what}.zip").format(**{
                   "year": year,
                   "what": what,
                   "WHAT": what.upper(),
                   "fips": fips,
                   "top": top,
               })

    download_file(url, where)



def download_state_leg_bounds():
    for fip in FIPS:
        download_census_file("TIGERrd13_st", fip, "sldl",
                             "13", "downloads/sldl-13")
        download_census_file("TIGERrd13_st", fip, "sldu",
                             "13", "downloads/sldu-13")

        download_census_file("TIGER2012", fip, "sldl",
                             "2012", "downloads/sldl-12")

        download_census_file("TIGER2012", fip, "sldu",
                             "2012", "downloads/sldu-12")

    return [extract_cwd(path=x) for x in ["downloads/sldl-13",
                                   "downloads/sldu-13",
                                   "downloads/sldl-12",
                                   "downloads/sldu-12"]]


def list_files(*flags):
    files = os.listdir('.')
    for _file in files:
        for flag in flags:
            if _file.endswith(flag):
                yield _file


def extract_cwd(path=None):
    pop = os.path.abspath(os.getcwd())
    if path:
        os.chdir(path)
    dirname = os.path.basename(os.getcwd())

    for filename in glob.glob('*.zip'):
        os.system('unzip -o %s' % filename)

    for path in list_files("dbf", "prj", "shp", "xml", "shx"):
        os.renames(path, "../../shapefiles/{dirname}/{path}".format(**locals()))


    os.chdir(pop)


def download_counties():
    for fip in FIPS:
        download_census_file("TIGERrd13_st", fip, "county10",
            "13", "downloads/county-13")

    extract_cwd("downloads/county-13")


def download_places():
    for fip in FIPS:
        download_census_file("TIGERrd13_st", fip, "place10",
            "13", "downloads/place-13")

    extract_cwd("downloads/place-13")


def download_fed_leg_bounds():
    for fip in FIPS:
        download_census_file("TIGERrd13_st", fip, "cd111",
                             "13", "downloads/cd-111")
        download_census_file("TIGERrd13_st", fip, "cd113",
                             "13", "downloads/cd-113")

    extract_cwd("downloads/cd-113")
    extract_cwd("downloads/cd-111")



def download_zcta():
    download_file(
        "ftp://ftp2.census.gov/geo/tiger/" 
        "TIGERrd13_st/nation/tl_rd13_us_zcta510.zip", 
        "downloads/zcta-13")
    extract_cwd("downloads/zcta-13")



download_places()
download_state_leg_bounds()
download_fed_leg_bounds()
download_counties()
download_zcta()
