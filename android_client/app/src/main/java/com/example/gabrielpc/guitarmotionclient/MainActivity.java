package com.example.gabrielpc.guitarmotionclient;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.bluetooth.*;
import android.util.Log;

import java.io.IOException;
import java.io.OutputStream;
import java.util.Set;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private final static int REQUEST_ENABLE_BT = 1;
    private BluetoothDevice host;
    private UUID uuid = UUID.fromString("5E66F20D-7079-472C-B8C3-97221B7C67F7");
    private OutputStream output_stream;

    private final byte COMMAND_NONE          = 0x00;
    private final byte COMMAND_JOLT_UP       = 0x01;
    private final byte COMMAND_JOLT_DOWN     = 0x02;
    private final byte COMMAND_NECK_UP       = 0x03;
    private final byte COMMAND_NECK_STRAIGHT = 0x04;
    private final byte COMMAND_NECK_DOWN     = 0x05;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    output_stream.write(COMMAND_JOLT_UP);
                }
                catch (IOException e) {
                    Log.d("Bluetooth", "Teste nao foi enviado");
                }
            }
        });

        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            Log.d("Bluetooth", "Bluetooth nao eh suportado");
        }
        else {
            Log.d("Bluetooth", "Bluetooth suportado");
        }

        if (!mBluetoothAdapter.isEnabled()) {
            // Bluetooth not active, ask the user to turn it on
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
            Log.d("Bluetooth", "Bluetooth ativado");
        }

        if (!mBluetoothAdapter.isEnabled()) {
            Log.d("Bluetooth", "Bluetooth nao ativado");
        }

        // FIXME: 10/22/2016
        // For now, assume that the host and this device are paired


        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
        // If there are paired devices
        if (pairedDevices.size() > 0) {
            for (BluetoothDevice device : pairedDevices) {
                // FIXME: 10/22/2016
                // For now, assume that the first device paired is the host
                host = device;
                Log.d("Bluetooth", "Host selecionado: " + host.getName());
                break;
            }
        }
        else {
            Log.d("Bluetooth", "Host nao selecionado");
        }

        // Now that we know the host, create the socket
        BluetoothSocket btsocket = null;
        try {
            btsocket = host.createRfcommSocketToServiceRecord(uuid);
        }
        catch (IOException e) {
            Log.d("Bluetooth", "Nao foi possivel criar o socket");
        }

        // And try to connect it
        try {
            // Connect the device through the socket. This will block
            // until it succeeds or throws an exception
            Log.d("Bluetooth", "Tentando conectar o socket");
            btsocket.connect();
        } catch (IOException connectException) {
            // Unable to connect; close the socket and get out
            try {
                Log.d("Bluetooth", "Nao foi possivel conectar o socket");
                btsocket.close();
            } catch (IOException closeException) { }
        }
        if (btsocket.isConnected()) {
            Log.d("Bluetooth","Socket conectado");
        }
        else {
            Log.d("Bluetooth", "Socket nao conectado");
        }

        try {
            output_stream = btsocket.getOutputStream();
        }
        catch (IOException e) {
            Log.d("Bluetooth", "Stream de output nao foi criada");
        }

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
