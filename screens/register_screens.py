def register_screens(sm):
    from screens.initial_screen import InitialScreen
    from screens.select_screen import SelectScreen
    from screens.deploy_screen import DeployScreen
    from screens.battle_screen import BattleScreen
    from screens.final_screen import FinalScreen

    sm.register("initial", InitialScreen)
    sm.register("select", SelectScreen)
    sm.register("deploy", DeployScreen)
    sm.register("battle", BattleScreen)
    sm.register("final", FinalScreen)
