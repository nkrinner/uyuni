# SUSE Manager for Retail build trigger
#
{%- set root_dir   = '/var/lib/Kiwi/' + pillar.get('build_id') %}
{%- set dest_dir   = root_dir + '/images.build' %}
{%- set build_id  = pillar.get('build_id') %}

# the goal is to collect all information required for
# saltboot image pillar

mgr_inspect_kiwi_image:
  mgrcompat.module_run:
    - name: kiwi_info.inspect_image
    - dest: {{ dest_dir }}
    - build_id: {{ build_id }}

mgr_kiwi_cleanup:
  cmd.run:
    - name: "rm -rf '{{ root_dir }}'"
    - require:
      - mgrcompat: mgr_inspect_kiwi_image
