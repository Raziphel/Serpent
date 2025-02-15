
###########################################################################
######################## ADMINISTRATIVE / MODERATION ######################
###########################################################################

CREATE TABLE moderation (
    user_id bigint NOT NULL,
    adult boolean DEFAULT false,
    image_banned boolean DEFAULT false,
    PRIMARY KEY (user_id)
);

CREATE TABLE user_link (
    discord_id BIGINT NOT NULL,
    steam_id VARCHAR(255) NOT NULL,
    PRIMARY KEY (discord_id, steam_id)
);


CREATE TABLE lottery (
    lottery_id BIGINT NOT NULL,
    last_winner_id BIGINT,
    last_amount INT,
    coins INT,
    lot_time TIMESTAMP,
    last_msg_id INT,
    PRIMARY KEY (lottery_id)
);


#############################################################################
############################## USER VALUES ##################################
#############################################################################

CREATE TABLE levels (
    user_id bigint NOT NULL,
    level integer NOT NULL DEFAULT 0,
    exp integer NOT NULL DEFAULT 0,
    last_xp timestamp,
    PRIMARY KEY (user_id)
);

CREATE TABLE currency (
    user_id bigint NOT NULL,
    coins integer DEFAULT 0,
    tickets integer DEFAULT 0,
    PRIMARY KEY (user_id)
);

CREATE TABLE daily (
    user_id bigint NOT NULL,
    daily integer NOT NULL DEFAULT 0,
    last_daily TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE items (
    user_id bigint NOT NULL,
    daily_saver integer NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);


#############################################################################
########################## USER TRACK / RECORDS #############################
#############################################################################

CREATE TABLE tracking (
    user_id bigint NOT NULL,
    messages integer DEFAULT 0,
    vc_mins integer DEFAULT 0,
    color integer,
    last_massage timestamp,
    PRIMARY KEY (user_id)
);

CREATE TABLE coins_record (
    user_id bigint NOT NULL,
    earned integer DEFAULT 0,
    spent integer DEFAULT 0,
    taxed integer DEFAULT 0,
    lost integer DEFAULT 0,
    stolen integer DEFAULT 0,
    gifted integer DEFAULT 0,
    given integer DEFAULT 0,
    PRIMARY KEY (user_id)
);

CREATE TABLE seasonal (
    user_id bigint NOT NULL,
    presents_given integer DEFAULT 0,
    presents_coins_given integer DEFAULT 0,
    PRIMARY KEY (user_id)
);


