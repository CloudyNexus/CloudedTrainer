def get_all_trainers():
    """Get all available trainer classes"""
    from trainers.csgo_trainer import CSGOTrainer
    from trainers.dota2_trainer import Dota2Trainer
    from trainers.minecraft_trainer import MinecraftTrainer
    from trainers.minecraft_dungeons_trainer import MinecraftDungeonsTrainer
    from trainers.tf2_trainer import TF2Trainer
    from trainers.terraria_trainer import TerrariaTrainer
    
    # Create instances of each trainer with a None memory manager (will be set later)
    return [
        CSGOTrainer(None),
        Dota2Trainer(None),
        MinecraftTrainer(None),
        MinecraftDungeonsTrainer(None),
        TF2Trainer(None),
        TerrariaTrainer(None)
    ]
