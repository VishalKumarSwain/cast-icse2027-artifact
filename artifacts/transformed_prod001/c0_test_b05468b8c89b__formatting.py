def deps_install(
    app,
    ref_or_path,
    install_folder,
    base_folder,
    graph_info,
    remotes=None,
    build_modes=None,
    update=False,
    manifest_folder=None,
    manifest_verify=False,
    manifest_interactive=False,
    generators=None,
    no_imports=False,
    create_reference=None,
    keep_build=False,
    recorder=None,
    lockfile_node_id=None,
    is_build_require=False,
    add_txt_generator=True,
    require_overrides=None,
    conanfile_path=None,
    test=None,
):
    out, user_io, graph_manager, cache = (
        app.out,
        app.user_io,
        app.graph_manager,
        app.cache,
    )
    remote_manager, hook_manager = app.remote_manager, app.hook_manager
    profile_host, profile_build = graph_info.profile_host, graph_info.profile_build
    if profile_build:
        out.info("Configuration (profile_host):")
        out.writeln(profile_host.dumps())
        out.info("Configuration (profile_build):")
        out.writeln(profile_build.dumps())
    else:
        out.info("Configuration:")
        out.writeln(profile_host.dumps())
    deps_graph = graph_manager.load_graph(
        ref_or_path,
        create_reference,
        graph_info,
        build_modes,
        False,
        update,
        remotes,
        recorder,
        lockfile_node_id=lockfile_node_id,
        is_build_require=is_build_require,
        require_overrides=require_overrides,
    )
    graph_lock = graph_info.graph_lock
    root_node = deps_graph.root
    conanfile = root_node.conanfile
    if root_node.recipe == RECIPE_VIRTUAL:
        out.highlight("Installing package: %s" % str(ref_or_path))
    else:
        conanfile.output.highlight("Installing package")
    print_graph(deps_graph, out)
    try:
        if cross_building(conanfile):
            settings = get_cross_building_settings(conanfile)
            message = "Cross-build from '%s:%s' to '%s:%s'" % settings
            out.writeln(message, Color.BRIGHT_MAGENTA)
    except ConanException:
        pass
    installer = BinaryInstaller(app, recorder=recorder)
    build_modes = BuildMode(build_modes, out)
    installer.install(
        deps_graph,
        remotes,
        build_modes,
        update,
        profile_host,
        profile_build,
        graph_lock,
        keep_build=keep_build,
    )
    graph_lock.complete_matching_prevs()
    if manifest_folder:
        manifest_manager = ManifestManager(
            manifest_folder, user_io=user_io, cache=cache
        )
        for node in deps_graph.nodes:
            if node.recipe in (RECIPE_CONSUMER, RECIPE_VIRTUAL):
                continue
            retrieve_exports_sources(
                remote_manager, cache, node.conanfile, node.ref, remotes
            )
        manifest_manager.check_graph(
            deps_graph, verify=manifest_verify, interactive=manifest_interactive
        )
        manifest_manager.print_log()
    if hasattr(conanfile, "layout") and not test:
        conanfile.folders.set_base_install(conanfile_path)
        conanfile.folders.set_base_imports(conanfile_path)
        conanfile.folders.set_base_generators(conanfile_path)
    else:
        conanfile.folders.set_base_install(install_folder)
        conanfile.folders.set_base_imports(install_folder)
        conanfile.folders.set_base_generators(base_folder)
    output = conanfile.output if root_node.recipe != RECIPE_VIRTUAL else out
    if install_folder:
        tmp = list(conanfile.generators)
        generators = set(generators) if generators else set()
        tmp.extend([g for g in generators if g not in tmp])
        if add_txt_generator:
            tmp.append("txt")
        conanfile.generators = tmp
        app.generator_manager.write_generators(
            conanfile, install_folder, conanfile.generators_folder, output
        )
        write_toolchain(conanfile, conanfile.generators_folder, output)
        if not isinstance(ref_or_path, ConanFileReference):
            content = normalize(conanfile.info.dumps())
            save(os.path.join(install_folder, CONANINFO), content)
            output.info("Generated %s" % CONANINFO)
            graph_info.save(install_folder)
            output.info("Generated graphinfo")
            graph_lock_file = GraphLockFile(profile_host, profile_build, graph_lock)
            graph_lock_file.save(os.path.join(install_folder, "conan.lock"))
        if not no_imports:
            run_imports(conanfile)
        if type(conanfile).system_requirements != ConanFile.system_requirements:
            call_system_requirements(conanfile, conanfile.output)
        if not create_reference and isinstance(ref_or_path, ConanFileReference):
            neighbours = deps_graph.root.neighbors()
            deploy_conanfile = neighbours[0].conanfile
            if hasattr(deploy_conanfile, "deploy") and callable(
                deploy_conanfile.deploy
            ):
                run_deploy(deploy_conanfile, install_folder)
