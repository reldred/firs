"""
  This file is part of FIRS Industry Set for OpenTTD.
  FIRS is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.
  FIRS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
  See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with FIRS. If not, see <http://www.gnu.org/licenses/>.
"""

print "[PYTHON] render pnml"

import codecs # used for writing files - more unicode friendly than standard open() module

import shutil
import sys
import global_constants
import os
currentdir = os.curdir
src_path = os.path.join(currentdir, 'src')
from multiprocessing import Pool
import subprocess

import global_constants as global_constants
import utils as utils
import firs
import cargos
from cargos import registered_cargos
import industries
from industries import registered_industries

# get args passed by makefile
repo_vars = utils.get_repo_vars(sys)

from chameleon import PageTemplateLoader # chameleon used in most template cases
# setup the places we look for templates
templates = PageTemplateLoader(os.path.join(src_path, 'templates'), format='text')
industry_templates = PageTemplateLoader(os.path.join(src_path, 'industries'), format='text')
header_item_templates = PageTemplateLoader(os.path.join(src_path, 'header_items'), format='text')

generated_pnml_path = os.path.join(firs.generated_files_path, 'pnml')
if not os.path.exists(generated_pnml_path):
    os.mkdir(generated_pnml_path)
generated_nml_path = os.path.join(firs.generated_files_path, 'nml')
if not os.path.exists(generated_nml_path):
    os.mkdir(generated_nml_path)
grf_nml = codecs.open(os.path.join(firs.generated_files_path, 'firs.nml'),'w','utf8')


def check_industry_needs_compiling(industry):
    test_industry_flag = repo_vars.get('test_industry', None)
    if test_industry_flag is None or test_industry_flag == '':
        return True
    elif test_industry_flag == industry.id:
        return True
    else:
        return False

def render_nml(filename):
    gcc_call_args = ['gcc',
                      '-D',
                      'REPO_REVISION='+str(repo_vars['repo_version']),
                      '-C',
                      '-E',
                      '-nostdinc',
                      '-x',
                      'c-header',
                      'generated/pnml/' + filename + '.pnml',
                      '-o',
                      'generated/nml/' + filename + '.nml']
    subprocess.call(gcc_call_args)


def render_nfo(filename):
    nmlc_call_args = ['nmlc',
                      '--lang-dir=lang',
                      #'--quiet',
                      '--nfo',
                      'generated/nfo/' + filename + '.nfo',
                      'generated/nml/' + filename + '.nml']
    subprocess.call(nmlc_call_args)


def render_header_item_pnml(header_item):
    print "Rendering " + header_item
    template = header_item_templates[header_item + '.pypnml']
    pnml = codecs.open(os.path.join(generated_pnml_path, header_item + '.pnml'), 'w','utf8')
    pnml.write(utils.unescape_chameleon_output(template(registered_industries=registered_industries,
                                        registered_cargos=registered_cargos, global_constants=global_constants,
                                        utils=utils, sys=sys, generated_pnml_path=generated_pnml_path)))
    pnml.close()


def render_cargo_pnml(cargo):
    # save the results of templating
    pnml_file = codecs.open(os.path.join(generated_pnml_path, cargo.id + '.pnml'), 'w','utf8')
    pnml_file.write(cargo.render_pnml())
    pnml_file.close()


def render_industry_pnml(industry):
    if check_industry_needs_compiling(industry):
        # save the results of templating
        pnml_file = codecs.open(os.path.join(generated_pnml_path, industry.id + '.pnml'), 'w','utf8')
        pnml_file.write(industry.render_pnml())
        pnml_file.close()


def render_dispatcher(items, renderer):
    if repo_vars.get('no_mp', None) == 'True':
        for item in items:
            renderer(item)
    else:
        pool = Pool(processes=16) # 16 is an arbitrary amount that appears to be fast without blocking the system
        pool.map(renderer, items)
        pool.close()
        pool.join()


def link_nml(item, dep_path, split=None):
    #dep_timestamps_new[dep_path] = os.stat(dep_path).st_mtime
    item_nml = codecs.open(os.path.join('generated', 'nml', item + '.nml'),'r','utf8').read()
    """
    if split is not None:
        # fragile split on some specific nfo, may break; assumes a right-split only
        if split in item_nfo:
            item_nfo = item_nfo.split(split)[1]
    """
    grf_nml.write(item_nml)


def main():
    header_items = ['checks','conditions','header','parameters', 'disable_default_cargos', 'cargo_table']

    if repo_vars.get('no_mp', None) == 'True':
        utils.echo_message('Multiprocessing disabled: (NO_MP=True)')

    print "Rendering nml"
    render_dispatcher(header_items, renderer=render_header_item_pnml)
    render_dispatcher(registered_cargos, renderer=render_cargo_pnml)
    render_dispatcher(industries.registered_industries, renderer=render_industry_pnml)

    print "Rendering nml from pnml"
    # render nml from pnml
    render_dispatcher(header_items, renderer=render_nml)
    render_dispatcher([cargo.id for cargo in registered_cargos], renderer=render_nml)
    render_dispatcher([industry.id for industry in industries.registered_industries], renderer=render_nml)

    # render nfo from nml
    # !! nothing yet !!

    # linker
    print "Linking nml"
    # !! replace second param to link_nml with file path
    for header_item in header_items:
        link_nml(header_item, header_item, split=None)
    for cargo in registered_cargos:
        link_nml(cargo.id, cargo.id, split=None)
    for industry in industries.registered_industries:
        if check_industry_needs_compiling(industry):
            link_nml(industry.id, industry.id, split=None)
    grf_nml.close()
    """
    dep_timestamps_file = codecs.open(dep_timestamps_path, 'w', 'utf8')
    dep_timestamps_file.write(json.dumps(dep_timestamps_new))
    dep_timestamps_file.close()
    """

if __name__ == '__main__':
    main()
