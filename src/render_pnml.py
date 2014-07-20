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

# get args passed by makefile
repo_vars = utils.get_repo_vars(sys)


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


def render_industry(industry):
    # save the results of templating
    pnml_file = codecs.open(os.path.join(generated_pnml_path, industry.id + '.pnml'), 'w','utf8')
    pnml_file.write(industry.render_pnml())
    pnml_file.close()
    render_nml(industry.id)


def render_header_item_pnml(header_item):
    print "Rendering " + header_item
    template = header_item_templates[header_item + '.pypnml']
    pnml = codecs.open(os.path.join(generated_pnml_path, header_item + '.pnml'), 'w','utf8')
    pnml.write(utils.unescape_chameleon_output(template(registered_industries=registered_industries, global_constants=global_constants,
                                                utils=utils, sys=sys, generated_pnml_path=generated_pnml_path)))
    pnml.close()


def main():
    header_items = ['checks','conditions','header','parameters']

    if repo_vars.get('no_mp', None) == 'True':
        utils.echo_message('Multiprocessing disabled: (NO_MP=True)')

    if repo_vars.get('no_mp', None) == 'True':
        for header_item in header_items:
            render_header_item_pnml(header_items)
    else:
        pool = Pool(processes=16) # 16 is an arbitrary amount that appears to be fast without blocking the system
        pool.map(render_header_item_pnml, header_items)
        pool.close()
        pool.join()

    template = templates['registered_cargos.pypnml']
    templated_pnml = utils.unescape_chameleon_output(template(registered_cargos=registered_cargos, global_constants=global_constants))
    # save the results of templating
    pnml = codecs.open(os.path.join(generated_pnml_path, 'registered_cargos.pnml'), 'w','utf8')
    pnml.write(templated_pnml)
    pnml.close()
    render_nml('registered_cargos')

    if repo_vars.get('no_mp', None) == 'True':
        for industry in industries.registered_industries:
            render_industry(industry)
    else:
        pool = Pool(processes=16) # 16 is an arbitrary amount that appears to be fast without blocking the system
        pool.map(render_industry, industries.registered_industries)
        pool.close()
        pool.join()

    for header_item in header_items:
        render_nml(header_item)

    # linker
    print "Linking"
    template = header_item_templates['firs.pypnml']
    firs_pnml = codecs.open(os.path.join(firs.generated_files_path, 'firs.pnml'), 'w','utf8')
    firs_pnml.write(utils.unescape_chameleon_output(template(registered_industries=registered_industries, global_constants=global_constants,
                                                utils=utils, sys=sys, generated_pnml_path=generated_pnml_path)))
    firs_pnml.close()

    render_header_item_pnml('firs')
    gcc_call_args = ['gcc',
                      '-D',
                      'REPO_REVISION='+str(repo_vars['repo_version']),
                      '-C',
                      '-E',
                      '-nostdinc',
                      '-x',
                      'c-header',
                      'generated/firs.pnml',
                      '-o',
                      'generated/firs.nml']
    subprocess.call(gcc_call_args)


if __name__ == '__main__':
    main()
