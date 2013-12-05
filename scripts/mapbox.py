import os
import sys
import json
import random
import itertools
import shapefile
from shapely.geometry import Polygon
from shapely.geos import PredicateError

from shapefiles.definitions import STATE_FIPS


def generate_mss(mss_id, shpfile, selector=None):
    shp = shapefile.Reader(shpfile)

    # find the position of the selector in fields
    candidate_selectors = (selector,) if selector else ('SLDLST', 'SLDUST')
    for fpos, field in enumerate(shp.fields):
        if field[0] in candidate_selectors:
            # the selector pos is 1 less than the pos in fields
            selector = field[0]
            spos = fpos - 1

    # create dict of selectors to polygons
    shapes = {}
    for rec, shape in zip(shp.records(), shp.shapes()):
        if rec[spos] == 'ZZZ':
            continue
        if shape.shapeType in (shapefile.POLYGON, shapefile.POLYGONZ):
            shapes[rec[spos]] = Polygon(shape.points)
        else:
            raise Exception("Unknown Shape Type: %s" % shape.shapeType)

    # color choices
    all_colors = ('@c1', '@c2', '@c3', '@c4', '@c5', '@c6', '@c7', '@c8', '@c9')
    colors = itertools.cycle(all_colors)

    shapes = shapes.items()

    is_well_colored = False
    while not is_well_colored:
        # shuffle the shapes
        random.shuffle(shapes)

        # assume we succeed
        is_well_colored = True

        # pick a color
        shape_colors = {}
        for name1, shape1 in shapes:
            disallowed_colors = set([None])
            # find overlapping colors
            for name2, shape2 in shapes:
                try:
                    if name1 != name2 and shape1.intersects(shape2):
                        disallowed_colors.add(shape_colors.get(name2))
                except PredicateError:
                    # not sure why these happen, but we'll count them as collisions
                    disallowed_colors.add(shape_colors.get(name2))
            # pick a color that matches
            proposed_color = None
            if len(disallowed_colors) == 10:
                print ("couldn't color", name1)
                is_well_colored = False
                break
            else:
                while proposed_color in disallowed_colors:
                    proposed_color = colors.next()
            shape_colors[name1] = proposed_color

    #for color in all_colors:
    #    print color, shape_colors.values().count(color)

    # write the .mss
    mss = """{0} {{ line-color: #999; line-width: 0.5; polygon-opacity: 0.5; }}
@c1: #f3b05d;
@c2: #b3bf7e;
@c3: #8cbcb5;
@c4: #e1582c;
@c5: #5e6f3e;
@c6: #698784;
@c7: #932700;
@c8: #7f985e;
@c9: #204e50;
\n
{0}[{1}="ZZZ"] {{ polygon-opacity: 0; line-opacity: 0; }}
\n
""".format(mss_id, selector)
    return mss + '\n'.join(
        '{0}[{1}="{2}"] {{ polygon-fill: {3}; }}'.format(mss_id, selector,
                                                         id, color)
        for id, color in sorted(shape_colors.iteritems()))


def generate_mml(shpfile, state=None, chamber=None, selector=None):
    shp = shapefile.Reader(shpfile)
    bbox = list(shp.bbox)
    if bbox[0] > 180:
        bbox = [-180, -85, 180, 85]

    # figure out chamber from fields
    if not chamber:
        if shp.fields[2][0] == 'SLDLST':
            chamber = 'lower'
        elif shp.fields[2][0] == 'SLDUST':
            chamber = 'upper'

    # figure out state from FIPS code in a record
    if not state and shp.fields[1][0] == 'STATEFP':
        state = STATE_FIPS[shp.record(0)[0]]

    projname = state + chamber

    mml = {'format': 'png', 'metatile': 2, 'minzoom': 4, 'maxzoom': 12,
           'description': '', 'attribution': '', 'legend': '',
           'Stylesheet': ["style.mss"],
           'name': projname, 'bounds': bbox,
           'srs': "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"}
    mml['center'] = [(bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2, 6]
    mml['Layer'] = [{'geometry': 'polygon', 'id': 'districts', 'class': '',
                     'Datasource': {'file': '../../'+shpfile}, 'extent': bbox,
                    'srs-name': 'autodetect', 'srs': '', 'advanced': {},
                     'name': 'districts'}]

    mml['interactivity'] = {'layer': 'districts',
                            'template_teaser': '{{NAMELSAD}}'}

    # make dir
    os.makedirs(os.path.join('project', projname))
    # write mml
    json.dump(mml, open(os.path.join('project', projname, 'project.mml'), 'w'), indent=2)
    # write mss
    mss = generate_mss('#districts', shpfile, selector)
    open(os.path.join('project', projname, 'style.mss'), 'w').write(mss)


def main ():
    arg = sys.argv[1]
    generate_mml('shapefiles/sldl/PVS_12_v2_sldl_%s.shp' % arg)
    generate_mml('shapefiles/sldu/PVS_12_v2_sldu_%s.shp' % arg)


if __name__ == "__main__":
    main()
